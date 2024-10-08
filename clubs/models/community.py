from django.db import models
class Community(models.Model):
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, related_name="community_posts")  # 클럽과 1:N 관계
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="community_posts")  # 작성자와 1:N 관계
    post_content = models.TextField(blank=True, null=True)  # 게시물 텍스트
    image = models.ImageField(upload_to="community_images/", blank=True, null=True)  # 이미지 파일 저장
    created_at = models.DateTimeField(auto_now_add=True)  # 게시물 생성 시간 자동 기록

    def __str__(self):
        return f"Post by {self.user.username} in {self.club.name}"