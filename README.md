# Onsen Development Setup

1. Install [python v 2.7.x] (https://www.python.org/downloads/)
2. Update PIP to current release, if this fails check your internet settings: 

	> pip install --upgrade pip

3. Unpack project files into its own folder.
4. Update environment with the required dependencies with the command command:

	>  pip install -r requirements.txt
	
5. Update the local_settings.py file with the local settings.
6. Populate the Database, this will install the tables for the supporting apps.

	> python manage.py migrate
	
7. Run the MakeMigrations command to analyze the Database and generate required new tables:

	> python manage.py makemigrations
	
8. Update the Database with the new migration:

	> python manage.py migrate

9. Create the first Superuser Account:

	> python manage.py createsuperuser 
	
10. Start development server.

	> python manage.py runserver
	
11. The project will now be available at (http://127.0.0.1:8000/)
