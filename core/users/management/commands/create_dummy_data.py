import random
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from connections.models import Connection
from rewards.models import Reward

class Command(BaseCommand):
    help = 'Creates dummy data for the application'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        User.objects.all().delete()
        Connection.objects.all().delete()
        Reward.objects.all().delete()

        self.stdout.write('Creating new data...')

        # --- Create Users ---
        users = []
        # Create the Demo User first
        demo_user = User.objects.create_user(
            username='guest',
            password='guestpassword',
            name='성시경',
            email='guest@example.com',
            province_name='서울특별시',
            city_name='강남구',
            manner_temperature=36.5,
            company_name='화피자',
            job_title='아티스트',
            school_name='화피자 대학교'
        )
        users.append(demo_user)

        first_names = ['민준', '서연', '지후', '예준', '서윤', '하준', '지아', '도윤', '시우', '서아']
        last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
        provinces = {
            '서울특별시': ['강남구', '마포구', '종로구'],
            '경기도': ['수원시', '성남시', '고양시']
        }

        for i in range(1, 20):
            first = random.choice(first_names)
            last = random.choice(last_names)
            province = random.choice(list(provinces.keys()))
            city = random.choice(provinces[province])
            user = User.objects.create_user(
                username=f'user{i}',
                password='password123',
                name=f'{last}{first}',
                email=f'user{i}@example.com',
                province_name=province,
                city_name=city,
                manner_temperature=round(random.uniform(30.0, 50.0), 1)
            )
            users.append(user)
        
        self.stdout.write(f'{len(users)} users created.')

        # --- Create Connections ---
        connection_count = 0
        for i in range(len(users)):
            # Each user sends 1-3 connection requests
            num_requests = random.randint(1, 3)
            for _ in range(num_requests):
                # Cannot connect to self
                to_user_index = random.randint(0, len(users) - 1)
                if i == to_user_index:
                    continue
                
                to_user = users[to_user_index]
                from_user = users[i]

                # Avoid duplicate connections
                if Connection.objects.filter(from_user=from_user, to_user=to_user).exists() or \
                   Connection.objects.filter(from_user=to_user, to_user=from_user).exists():
                   continue

                Connection.objects.create(
                    from_user=from_user,
                    to_user=to_user,
                    status=random.choice(['PENDING', 'CONNECTED', 'CONNECTED']) # Higher chance of being connected
                )
                connection_count += 1

        self.stdout.write(f'{connection_count} connections created.')

        # --- Create Rewards ---
        rewards_data = [
            {'name': '첫 친구 맺기', 'description': '첫 친구를 맺으면 달성할 수 있습니다.', 'points_required': 10},
            {'name': '열정적인 활동가', 'description': '10명과 관계를 맺으면 달성할 수 있습니다.', 'points_required': 100},
            {'name': '동네 인싸', 'description': '우리 동네에서 5명 이상의 친구를 만드세요.', 'points_required': 50},
        ]

        for r_data in rewards_data:
            Reward.objects.create(**r_data)
        
        self.stdout.write(f'{len(rewards_data)} rewards created.')

        self.stdout.write(self.style.SUCCESS('Successfully created dummy data.'))
