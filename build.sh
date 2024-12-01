set -o errexit
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations accounts
python manage.py makemigrations economy
python manage.py makemigrations feedback_and_report

python manage.py migrate

if [[$CREATE_SUPERUSER ]];
then
python manage.py createsuperuser --no-input
fi