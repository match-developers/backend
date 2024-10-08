import openai
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

# from accounts.models.users import User, UserStatistics  # 문자열 참조로 변경
# from sportsgrounds.models.sports_ground import SportsGround
# from sportsgrounds.models.facilities import Facilities
# from leagues.models.league import League
# from tournaments.models.tournament import Tournament
from matchmaking.models.team import Team
from newsfeed.models.newsfeed import NewsfeedPost
from newsfeed.models.match_post import MatchPost

from model_utils.models import TimeStampedModel

# Match 상태를 나타내는 choices (예정됨, 진행 중, 완료됨 등)
STATUS_CHOICES = [
    ("pending", "Pending"),
    ("scheduled", "Scheduled"),
    ("ongoing", "Ongoing"),
    ("completed", "Completed"),
    ("canceled", "Canceled"),
]


class Match(TimeStampedModel):
    sports_ground = models.ForeignKey('sportsgrounds.SportsGround', on_delete=models.CASCADE)
    facility = models.ForeignKey('sportsgrounds.Facilities', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration = models.DurationField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    match_type = models.CharField(max_length=50, choices=[("single", "Single"), ("league", "League"), ("tournament", "Tournament")], default="single")
    league = models.ForeignKey('leagues.League', on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    total_spots = models.IntegerField()
    participants = models.ManyToManyField('matchmaking.TeamPlayer', related_name="matches", blank=True)
    referees = models.ManyToManyField('accounts.User', related_name="refereed_matches", blank=True)
    spectators = models.ManyToManyField('accounts.User', related_name="spectated_matches", blank=True)
    winning_method = models.ForeignKey('WinningMethod', on_delete=models.CASCADE, null=True, blank=True)
    is_private = models.BooleanField(default=False)  # 공개/비공개 매치 여부
    join_requests = models.ManyToManyField('accounts.User', related_name="join_requests", blank=True)  # 참가 요청 리스트

    @property
    def available_spots(self):
        return self.total_spots - self.participants.count()

    def prevent_overlap(self, user):
        """Prevent user from joining multiple matches at the same time"""
        ongoing_matches = Match.objects.filter(
            participants__user=user,
            start_time__lt=self.start_time + self.duration,
            start_time__gt=self.start_time - self.duration,
        )
        if ongoing_matches.exists():
            raise ValidationError("You cannot join another match that overlaps with your current match.")

    def assign_teams(self):
        if self.match_type == 'club':
            # If it's a club match, assign clubs directly
            club_teams = list(set(participant.user.club for participant in self.participants if participant.user.club))
            if len(club_teams) == 2:
                team_1 = Team.objects.create(name=club_teams[0].name, club=club_teams[0], is_red_team=True)
                team_2 = Team.objects.create(name=club_teams[1].name, club=club_teams[1], is_red_team=False)
                for player in self.participants.all():
                    if player.user.club == club_teams[0]:
                        player.team = team_1
                    else:
                        player.team = team_2
                    player.save()
        else:
            # Assign default Red/Blue teams for individual matches
            red_team = Team.objects.create(name="Red Team", is_red_team=True)
            blue_team = Team.objects.create(name="Blue Team", is_red_team=False)
            participants = list(self.participants.all())
            for idx, player in enumerate(participants):
                if idx % 2 == 0:
                    player.team = red_team
                else: player.team = blue_team
                player.save()

    @classmethod
    def create_match(cls, creator, sports_ground, facility, price, start_time, duration, match_type, total_spots, league=None, tournament=None, winning_method=None):
        """
        매치 생성 메서드 (타임 슬롯을 기반으로 매치 생성)
        """
        match = cls.objects.create(
            creator=creator,
            sports_ground=sports_ground,
            facility=facility,
            price=price,
            start_time=start_time,
            duration=duration,
            match_type=match_type,
            total_spots=total_spots,
            league=league,
            tournament=tournament,
            winning_method=winning_method
        )
        # 매치 생성 시 뉴스피드 포스트 생성
        match.create_match_post()
        return match

    def start_match(self):
        """
        매치 시작 시 뉴스피드 업데이트 및 팔로워들에게 알림 전송
        """
        self.status = 'ongoing'
        self.save()

        participants = self.participants.all()
        for participant in participants:
            followers = participant.user.followers.all()
            for follower in followers:
                newsfeed_post = NewsfeedPost.objects.create(
                    newsfeed=follower.newsfeed,
                    post_type="match",
                    post_id=self.id,
                    post_content=f"{participant.user.username}님이 방금 매치를 시작했습니다."
                )
                MatchPost.objects.create(
                    match=self,
                    created_by=participant.user,
                    post_content=f"{participant.user.username}님이 방금 매치를 시작했습니다.",
                    newsfeed_post=newsfeed_post
                )

    def complete_match(self):
        """
        매치 완료 시 뉴스피드 업데이트 및 팔로워들에게 알림 전송
        """
        self.status = 'completed'
        self.save()

        participants = self.participants.all()
        for participant in participants:
            followers = participant.user.followers.all()
            for follower in followers:
                newsfeed_post = NewsfeedPost.objects.create(
                    newsfeed=follower.newsfeed,
                    post_type="match",
                    post_id=self.id,
                    post_content=f"{participant.user.username}님의 매치가 방금 끝났습니다."
                )
                MatchPost.objects.create(
                    match=self,
                    created_by=participant.user,
                    post_content=f"{participant.user.username}님의 매치가 방금 끝났습니다.",
                    newsfeed_post=newsfeed_post
                )

        # 기존 뉴스피드 포스트 업데이트
        newsfeed_post = NewsfeedPost.objects.get(post_id=self.id, post_type="match")
        newsfeed_post.post_content = f"Match completed."
        newsfeed_post.pinned = False
        newsfeed_post.save()


class WinningMethod(models.Model):
    points_needed = models.IntegerField()  # 승리 조건으로 필요한 포인트
    time_per_set = models.DurationField()  # 세트 당 시간 (타임 필드)
    sets = models.IntegerField()  # 세트 수
    points_per_action = models.JSONField()  # 각 행동에 따른 점수 (예: 골, 어시스트 등)
    additional_rules = models.TextField(null=True, blank=True)  # 추가 규칙

    def __str__(self):
        return f"Winning Method: {self.points_needed} points needed, {self.sets} sets"

class PressConference(models.Model):
    match = models.OneToOneField('matchmaking.Match', related_name="press_conference", on_delete=models.CASCADE)
    participants = models.ManyToManyField('matchmaking.TeamPlayer', related_name="press_conferences")
    questions = models.JSONField()  # ChatGPT API로 생성된 질문들 저장
    chat_log = models.JSONField(blank=True, null=True)  # 대화 기록 저장
    current_question_index = models.IntegerField(default=0)  # 현재 질문 인덱스

    def generate_questions(self):
        """
        ChatGPT API와 연동해 자동으로 질문을 생성하는 메서드.
        질문 목록을 self.questions에 저장함.
        """
        # OpenAI API 키 설정
        openai.api_key = settings.OPENAI_API_KEY

        # 프롬프트 작성
        prompt = f"다음 참가자들이 포함된 축구 경기를 위한 흥미로운 질문 5개를 생성해줘:\n"
        for player in self.match.participants.all():
            prompt += f"- {player.user.username}, stats: {player.user.user_statistics}\n"
        prompt += "질문들은 경기 및 선수들과 관련된 것이어야 합니다."

        # OpenAI API를 통해 질문 생성
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                n=5,
                stop=None,
                temperature=0.7,
            )

            # 생성된 질문을 JSON 형태로 저장
            generated_questions = [choice['text'].strip() for choice in response['choices']]
            self.questions = generated_questions
            self.save()
        except Exception as e:
            print(f"질문 생성 중 오류 발생: {e}")
            return None

    def create_prompt(self):
        """
        경기 참가자와 경기 세부 정보를 바탕으로 ChatGPT 프롬프트 생성.
        """
        match_info = f"{self.match.sports_ground.name}에서 시작하는 경기 정보."
        player_info = []

        for participant in self.participants.all():
            UserStatistics = apps.get_model('accounts', 'UserStatistics')  
            user_stats = UserStatistics.objects.get(user=participant.user)
            player_info.append(
                f"플레이어 {participant.user.username}: {user_stats.mp} 경기, {user_stats.wins} 승리, 매너 점수 {user_stats.manner}."
            )

        prompt = f"{match_info}\n참가자들:\n" + "\n".join(player_info)
        return prompt

    def ask_next_question(self):
        """
        Press Conference에서 다음 질문을 던짐.
        """
        if self.current_question_index == 0:
            intro_message = f"다가오는 경기의 기자회견에 오신 것을 환영합니다: {self.match.sports_ground.name}."
            self.current_question_index += 1
            self.save()
            return intro_message
        elif self.current_question_index <= len(self.questions):
            next_question = self.questions[self.current_question_index - 1]
            self.current_question_index += 1
            self.save()
            return next_question
        else:
            return "기자회견 질문이 끝났습니다. 자유롭게 토론을 이어가십시오."

    def process_answer(self, answer):
        """
        사용자가 답변을 제출하면, 대화 로그에 저장하고 다음 질문을 던짐.
        """
        if not self.chat_log:
            self.chat_log = []

        if self.current_question_index > 1:
            current_question = self.questions[self.current_question_index - 2]
            self.chat_log.append({
                "question": current_question,
                "answer": answer,
                "timestamp": timezone.now().isoformat(),
            })
        else:
            self.chat_log.append({
                "message": answer,
                "timestamp": timezone.now().isoformat(),
            })

        self.save()

        return self.ask_next_question()

class TeamTalk(models.Model):
    match = models.ForeignKey('matchmaking.Match', related_name="team_talks", on_delete=models.CASCADE)
    team = models.ForeignKey('matchmaking.TeamPlayer', related_name="team_talks", on_delete=models.CASCADE)
    chat_log = models.JSONField()

    def __str__(self):
        return f"{self.match} 경기 중 {self.team}의 팀 대화"
    
class MatchEvent(TimeStampedModel):
    EVENT_TYPES = (
        ('point', 'Point'),
        ('special_point', 'Special Point'),
        ('pause', 'Pause'),
        ('set_end', 'Set End'),
        ('match_end', 'Match End'),
    )

    match = models.ForeignKey('matchmaking.Match', related_name="events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey('matchmaking.TeamPlayer', on_delete=models.CASCADE)
    target_player = models.ForeignKey(
        'matchmaking.TeamPlayer', 
        related_name="target_events", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    def clean(self):
        # point 및 special point 이벤트는 대상이 필요함
        if self.event_type in ['point', 'special_point'] and not self.target_player:
            raise ValidationError("Point or Special Point events must have a target player.")
        # pause, set_end, match_end 이벤트는 대상이 없어야 함
        elif self.event_type in ['pause', 'set_end', 'match_end'] and self.target_player:
            raise ValidationError(f"{self.event_type} events should not have a target player.")

    def __str__(self):
        if self.event_type in ['point', 'special_point']:
            return f"{self.added_by} added {self.event_type} to {self.target_player} at {self.timestamp}"
        else:
            return f"{self.added_by} added {self.event_type} at {self.timestamp}"
    
class PlayerReview(models.Model):
    match = models.ForeignKey('matchmaking.Match', on_delete=models.CASCADE)  # 매치와 연결
    reviewer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_given')  # 리뷰 작성자
    player = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_received')  # 평가된 플레이어
    
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 매너 평가 (1~5)
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 성과 평가 (1~5)
    written_review = models.TextField(blank=True, null=True)  # 서면 리뷰 (선택 사항)

    def __str__(self):
        return f"Review for {self.player.username} by {self.reviewer.username}"

class GroundReview(models.Model):
    match = models.ForeignKey('matchmaking.Match', on_delete=models.CASCADE)  # 매치와 연결
    reviewer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)  # 리뷰 작성자
    ground = models.ForeignKey('sportsgrounds.SportsGround', on_delete=models.CASCADE)  # 평가된 구장

    quality = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 구장 품질 평가 (1~5)
    safety = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 안전성 평가 (1~5)
    support = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 지원 시설 평가 (1~5)
    written_review = models.TextField(blank=True, null=True)  # 서면 리뷰 (선택 사항)

    def __str__(self):
        return f"Review for {self.ground.name} by {self.reviewer.username}"