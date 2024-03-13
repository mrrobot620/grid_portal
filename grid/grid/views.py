from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages  # Import messages framework for displaying messages
from django.contrib.auth.decorators import login_required
from firebase_admin import credentials, initialize_app, storage, exceptions
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

# Initialize Firebase app and bucket
cred = credentials.Certificate(settings.FIREBASE_ADMIN_SDK_CREDENTIALS)
initialize_app(cred, {'storageBucket': 'smartbtprinter.appspot.com'})
bucket = storage.bucket()

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def home(request):
    sites = get_sites()
    return render(request, 'home.html', {"sites": sites})

def logout_view(request):
    logout(request)
    return redirect("login")

def get_sites():
    blobs = bucket.list_blobs()
    folder_names = set(blob.name.split('/')[0] for blob in blobs if '/' in blob.name)
    return folder_names

@login_required
def folder_detail(request, folder_name):
    blobs = bucket.list_blobs(prefix=folder_name)
    files = [{'name': blob.name.split('/')[-1], 'download_url': blob.generate_signed_url}
             for blob in blobs if blob.name.endswith('.csv')]
    return render(request, 'home.html', {'folder_name': folder_name, 'files': files})

@login_required
def upload_csv_to_storage(request, folder_name):
    if request.method == "POST" and request.FILES.get('csv_file'):
        try:
            csv_file = request.FILES['csv_file']
            csv_file.name = 'grid.csv'
            if csv_file.size > 5 * 1024 * 1024:  # 5 MB
                return HttpResponse("CSV file size exceeds the limit (5 MB).", status=400)
            blob = bucket.blob(folder_name + '/' + csv_file.name)
            blob.upload_from_file(csv_file)
            messages.success(request, "File uploaded successfully.")
        except exceptions.FirebaseError as e:
            messages.error(request, f"An error occurred while uploading CSV file: {e}")
    else:
        messages.error(request, "No CSV file provided.")
    return redirect('home')
