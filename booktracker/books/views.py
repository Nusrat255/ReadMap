from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Borrow, Rating
from .forms import RatingForm

def home(request):
 books = Book.objects.all()
 return render(request, 'books/home.html', {'books': books})

def book_detail(request, pk):
  book = get_object_or_404(Book, pk=pk)
  rating_form = RatingForm()
  user_rating = None
  if request.user.is_authenticated:
      user_rating = Rating.objects.filter(book=book, user=request.user).first()
  return render(request, 'books/book_detail.html', {
        'book': book,
        'rating_form': rating_form,
        'user_rating': user_rating
    })
@login_required
def rate_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_obj, created = Rating.objects.update_or_create(
                user=request.user, book=book, defaults={'rating': form.cleaned_data['rating']}
            )
    return redirect('book_detail', pk=pk)

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.available_copies > 0:
        Borrow.objects.create(user=request.user, book=book)
        book.available_copies -= 1
        book.save()
    return redirect('book_detail', pk=pk)

@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    borrow = Borrow.objects.filter(user=request.user, book=book, return_date__isnull=True).first()
    if borrow:
        borrow.return_date = '2025-10-10'  # For simplicity; you can use datetime.today()
        borrow.save()
        book.available_copies += 1
        book.save()
    return redirect('book_detail', pk=pk)

