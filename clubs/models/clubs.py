from django.db import models
# from accounts.models.users import User  # 문자열 참조로 대체
from newsfeed.models.newsfeed import NewsfeedPost

class Club(models.Model):
    name = models.CharField(max_length=255)  # 클럽 이름
    profile_photo = models.ImageField(upload_to='clubs/profile_photos/', null=True, blank=True)  # 프로필 사진
    bio = models.TextField(null=True, blank=True)  # 클럽 소개
    member_number = models.IntegerField(default=0)  # 멤버 수 (자동 계산됨)
    followers = models.JSONField(null=True, blank=True)  # 팔로워 목록 (JSON 형태)
    owner = models.ForeignKey('accounts.User', related_name="owned_club", on_delete=models.CASCADE)  # 클럽 소유자 (User 테이블과 연결)
        
    # 클럽 내에서 멤버별 권한을 관리하기 위한 필드 (JSON 형태로 저장)
    member_permissions = models.JSONField(default=dict, blank=True)
    
    # 권한 타입을 고정된 선택지로 설정
    PERMISSION_TYPES = (
        ('create_match', 'Create Match'),
        ('manage_team', 'Manage Team'),
        ('assign_owner', 'Assign Owner'),
        ('manage_requests', 'Manage Join Requests'),
    )

    # Join 요청을 관리할 수 있는 필드 (리스트 형태로 요청자들을 관리)
    join_requests = models.ManyToManyField('accounts.User', related_name="club_join_requests", blank=True)
    
    # 클럽 멤버들 (사용자가 클럽에 가입하거나 탈퇴할 때 사용)
    members = models.ManyToManyField('accounts.User', related_name="clubs_joined", blank=True)
    
    # 권한 필드
    match_creators = models.ManyToManyField('accounts.User', related_name="clubs_can_create_match", blank=True)  # 매치 생성 권한을 가진 멤버들
    team_managers = models.ManyToManyField('accounts.User', related_name="clubs_can_manage_team", blank=True)  # 팀을 관리할 권한을 가진 멤버들
    owner_assignees = models.ManyToManyField('accounts.User', related_name="clubs_can_assign_owner", blank=True)  # 소유자 권한을 부여할 수 있는 멤버들

    # 클럽 뉴스피드: 클럽이 참가하거나 생성한 매치, 리그, 토너먼트 게시물만 표시
    club_newsfeed = models.OneToOneField(
        'newsfeed.Newsfeed', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='club_newsfeed'
    )
    
    def __str__(self):
        return self.name

    def add_member(self, user):
        """
        사용자가 클럽에 가입할 때 호출되는 메서드.
        """
        if user not in self.members.all():
            self.members.add(user)
            self.member_number = self.members.count()  # 멤버 수 갱신
            self.save()

    def remove_member(self, user):
        """
        사용자가 클럽에서 탈퇴할 때 호출되는 메서드.
        """
        if user in self.members.all():
            self.members.remove(user)
            self.member_number = self.members.count()  # 멤버 수 갱신
            self.save()

    def get_club_newsfeed_posts(self):
        """
        클럽과 관련된 뉴스피드 포스트만 필터링하여 반환.
        """
        return NewsfeedPost.objects.filter(
            models.Q(creator=self.owner) |  # 클럽 소유자가 생성한 포스트
            models.Q(match__club=self) |  # 클럽이 참가한 매치 포스트
            models.Q(league__club=self) |  # 클럽이 참가한 리그 포스트
            models.Q(tournament__club=self)  # 클럽이 참가한 토너먼트 포스트
        ).distinct()

    def is_owner(self, user):
        """
        사용자가 클럽의 소유자인지 확인.
        """
        return self.owner == user

    def has_permission(self, user, permission_type):
        """
        사용자가 특정 권한을 가지고 있는지 확인.
        permission_type은 'create_match', 'manage_team', 'assign_owner', 'manage_requests' 등을 처리.
        """
        if self.is_owner(user):
            return True
        # 권한 확인 (member_permissions 필드에서 권한 정보를 확인)
        permissions = self.member_permissions.get(str(user.id), [])
        return permission_type in permissions

    def assign_permission(self, user, permission_type):
        """
        사용자에게 특정 권한을 부여하는 메서드.
        """
        if str(user.id) not in self.member_permissions:
            self.member_permissions[str(user.id)] = []
        if permission_type not in self.member_permissions[str(user.id)]:
            self.member_permissions[str(user.id)].append(permission_type)
        self.save()

    def remove_permission(self, user, permission_type):
        """
        사용자에게 부여된 특정 권한을 제거하는 메서드.
        """
        if str(user.id) in self.member_permissions:
            self.member_permissions[str(user.id)].remove(permission_type)
            if not self.member_permissions[str(user.id)]:
                del self.member_permissions[str(user.id)]
        self.save()

    def accept_join_request(self, user):
        """
        클럽 가입 요청을 수락하는 메서드.
        """
        if user in self.join_requests.all():
            self.join_requests.remove(user)
            self.add_member(user)
    
    def decline_join_request(self, user):
        """
        클럽 가입 요청을 거절하는 메서드.
        """
        if user in self.join_requests.all():
            self.join_requests.remove(user)