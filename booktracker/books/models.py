from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} rated {self.book.title}: {self.rating}"
