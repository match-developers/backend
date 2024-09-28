from django.db import models
from django.apps import apps

class ClubStatistics(models.Model):
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)  # Club과 1:1 관계
    mp = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points_scored = models.IntegerField(default=0)
    manner = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    performance = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    playstyle = models.CharField(max_length=255, blank=True, null=True)
    league = models.ForeignKey('leagues.League', on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.club.name} - Statistics"

    def update_match_stats(self, match_result, points):
        self.mp += 1
        self.points_scored += points

        if match_result == 'win':
            self.wins += 1
        elif match_result == 'draw':
            self.draws += 1
        elif match_result == 'loss':
            self.losses += 1

        self.save()

    def update_manner_score(self):
        members = self.club.members.all()
        total_manner = 0
        member_count = members.count()

        for member in members:
            user_stats = apps.get_model('accounts', 'UserStatistics').objects.get(user=member)
            total_manner += user_stats.manner

        self.manner = total_manner / member_count if member_count > 0 else 0.00
        self.save()

    def update_performance_score(self):
        members = self.club.members.all()
        total_performance = 0
        member_count = members.count()

        for member in members:
            user_stats = apps.get_model('accounts', 'UserStatistics').objects.get(user=member)
            total_performance += user_stats.performance

        self.performance = total_performance / member_count if member_count > 0 else 0.00
        self.save()