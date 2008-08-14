deploy:
	rsync -vzr --delete --exclude="*.pyc" --exclude="/lxml" --exclude=".svn" --exclude="/lektury.sqlite" --exclude="/settings.py" . zuber@continental.dreamhost.com:django_projects/wolnelektury
	ssh zuber@continental.dreamhost.com 'touch ~/wolnelektury.stepniowski.com/dispatch.fcgi'