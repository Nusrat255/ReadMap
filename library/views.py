from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Book, BorrowRecord, BookReview
from django.db import IntegrityError

# ------------------ Auth ------------------
def home(request):
    return render(request, 'library/home.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect('borrower')
    return render(request, 'library/signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print("Authenticated user:", user)  # ← Add this
        if user:
            ...
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('admin_books')
            else:
                return redirect('borrower')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'library/login.html')
def user_logout(request):
    logout(request)
    return redirect('home')

def password_reset_request(request):
    # Simulated reset (no email)
    if request.method == 'POST':
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            # In real app: send email with token
            messages.success(request, f"Password reset token for '{username}' is: 'RESET-{user.id}'. (This is simulated.)")
        except User.DoesNotExist:
            messages.error(request, "Username not found.")
    return render(request, 'library/password_reset.html')

def password_reset_done(request):
    return render(request, 'library/password_reset_done.html')

# ------------------ Admin ------------------
def admin_books(request):
    if not request.user.is_staff:
        return redirect('borrower')
    books = Book.objects.all()
    return render(request, 'library/admin_books.html', {'books': books})


def remove_book(request, book_id):
    if not request.user.is_staff:
        return redirect('borrower')
    Book.objects.filter(id=book_id).delete()
    return redirect('admin_books')

def add_book(request):
    if not request.user.is_staff:
        return redirect('borrower')
    if request.method == 'POST':
        title = request.POST['title'].strip()
        author = request.POST['author'].strip()
        category = request.POST.get('category', 'other')
        pdf_file = request.FILES.get('pdf_file')

        try:
            book = Book(
                title=title,
                author=author,
                category=category,
                pdf_file=pdf_file
            )
            book.save()
            messages.success(request, "Book added successfully!")
        except IntegrityError:
            messages.error(request, "This book (title + author) already exists!")
        return redirect('admin_books')
    return redirect('admin_books')
# ------------------ Borrower ------------------
def borrower_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    borrowed_records = BorrowRecord.objects.filter(user=user, returned=False)
    available_books = Book.objects.filter(available=True)
    borrowed_books = [r.book for r in borrowed_records]

    # Group borrowed books by category for reading history
    categories = {}
    for book in borrowed_books:
        cat = book.get_category_display()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(book)

    return render(request, 'library/borrower.html', {
        'available': available_books,
        'categories': categories,
        'user': user
    })

def borrow_book(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')
    book = get_object_or_404(Book, id=book_id, available=True)
    book.available = False
    book.save()
    BorrowRecord.objects.create(user=request.user, book=book)
    return redirect('borrower')

def return_book(request, record_id):
    if not request.user.is_authenticated:
        return redirect('login')
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user, returned=False)
    record.returned = True
    record.save()
    record.book.available = True
    record.book.save()
    return redirect('borrower')

# ------------------ Search & Review ------------------
def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    ) if query else Book.objects.none()
    return render(request, 'library/search_results.html', {'books': books, 'query': query})

def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        notes = request.POST.get('notes', '')
        review, created = BookReview.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={'rating': rating, 'notes': notes}
        )
        messages.success(request, "Review saved!")
        return redirect('borrower')
    # Pre-fill if already reviewed
    review = BookReview.objects.filter(user=request.user, book=book).first()
    return render(request, 'library/review_form.html', {'book': book, 'review': review})