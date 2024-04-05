from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, unique=False)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    ref_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name if full_name.strip() else self.username


class Poll(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    photos = models.ManyToManyField('PhotoModel', blank=True,  related_name='poll_photos')

    
    def user_can_vote(self, user):
        """
        Return False if user already voted
        """
        user_votes = user.vote_set.all()
        qs = user_votes.filter(poll=self)


        if qs.exists():
            return False
        return True

    @property
    def get_vote_count(self):
        return self.vote_set.count()

    def get_result_dict(self):
        res = []
        for choice in self.choice_set.all():
            d = {}
            alert_class = ['primary', 'secondary', 'success',
                           'danger', 'dark', 'warning', 'info']

            d['alert_class'] = secrets.choice(alert_class)
            d['text'] = choice.choice_text
            d['num_votes'] = choice.get_vote_count
            if not self.get_vote_count:
                d['percentage'] = 0
            else:
                d['percentage'] = (choice.get_vote_count /
                                   self.get_vote_count)*100

            res.append(d)
        return res

    def __str__(self):
        return self.text


class PhotoModel(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='poll_photos/')


class BackgroundModel(models.Model):
    title = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='background_photos/')
    photo_type = models.CharField(max_length=100, default='login_background')

    def __str__(self):
        return self.title


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_vote_count(self):
        return self.vote_set.count()

    def __str__(self):
        return f"{self.poll.text[:25]} - {self.choice_text[:25]}"


class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.poll.text[:15]} - {self.choice.choice_text[:15]} - {self.user.username}'


class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        (1, 'Проблема з оплатою'),
        (2, 'Проблема з підтримкою власників'),
        (3, 'Технічні проблеми з обладнанням'),
        (4, 'Проблема з інтернетом або зв\'язком'),
        (5, 'Проблема з комунікацією'),
        (7, 'Нещасний випадок або надзвичайна ситуація'),
        (8, 'Проблема з безпекою'),
        (9, 'Інша проблема'),
    ]

    category = models.IntegerField(choices=CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    from_user = models.TextField(null=True)

    def __str__(self):
        return f'Ticket {self.pk}'