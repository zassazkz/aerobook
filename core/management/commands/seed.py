import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Airport, Airplane, Flight, Seat

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # 1. Create Superuser
        if not User.objects.filter(email='admin@aerobook.kz').exists():
            User.objects.create_superuser(
                email='admin@aerobook.kz',
                username='admin',
                password='admin1234'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created'))

        # 2. Create Airports
        airports_data = [
            {'iata_code': 'ALA', 'name': 'Almaty International Airport', 'city': 'Almaty', 'country': 'Kazakhstan'},
            {'iata_code': 'NQZ', 'name': 'Nursultan Nazarbayev International Airport', 'city': 'Astana', 'country': 'Kazakhstan'},
            {'iata_code': 'DXB', 'name': 'Dubai International Airport', 'city': 'Dubai', 'country': 'UAE'},
            {'iata_code': 'IST', 'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey'},
            {'iata_code': 'FRA', 'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany'},
            {'iata_code': 'JFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
        ]

        airports = []
        for data in airports_data:
            airport, created = Airport.objects.get_or_create(iata_code=data['iata_code'], defaults=data)
            airports.append(airport)
            if created:
                self.stdout.write(f"Airport {airport.iata_code} created")

        # 3. Create Airplanes and Seats
        airplanes_data = [
            {'model': 'Boeing 737', 'total_rows': 30, 'seats_per_row': 6, 'business_rows': 3},
            {'model': 'Airbus A320', 'total_rows': 28, 'seats_per_row': 6, 'business_rows': 4},
            {'model': 'Boeing 787', 'total_rows': 35, 'seats_per_row': 6, 'business_rows': 5},
        ]

        seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        
        for data in airplanes_data:
            airplane, created = Airplane.objects.get_or_create(model=data['model'], defaults=data)
            if created:
                self.stdout.write(f"Airplane {airplane.model} created. Generating seats...")
                seats = []
                for row in range(1, data['total_rows'] + 1):
                    seat_class = 'business' if row <= data['business_rows'] else 'economy'
                    for letter in seat_letters[:data['seats_per_row']]:
                        seats.append(Seat(
                            airplane=airplane,
                            row=row,
                            number=letter,
                            seat_class=seat_class
                        ))
                Seat.objects.bulk_create(seats)
                self.stdout.write(f"Generated {len(seats)} seats for {airplane.model}")

        # 4. Create Flights
        airplanes = Airplane.objects.all()
        routes = [
            ('ALA', 'NQZ', 25000, 60000),
            ('NQZ', 'ALA', 25000, 60000),
            ('ALA', 'DXB', 80000, 150000),
            ('DXB', 'ALA', 80000, 150000),
            ('ALA', 'IST', 90000, 180000),
            ('NQZ', 'FRA', 120000, 250000),
            ('FRA', 'NQZ', 120000, 250000),
            ('ALA', 'JFK', 200000, 450000),
        ]

        now = timezone.now()
        
        for origin_code, dest_code, min_price, max_price in routes:
            origin = Airport.objects.get(iata_code=origin_code)
            destination = Airport.objects.get(iata_code=dest_code)
            
            # Create a flight for some random day in the next 30 days
            days_ahead = random.randint(1, 30)
            departure_time = now + timedelta(days=days_ahead, hours=random.randint(0, 23))
            arrival_time = departure_time + timedelta(hours=random.randint(2, 12))
            
            Flight.objects.create(
                airplane=random.choice(airplanes),
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=Decimal(random.randint(min_price, max_price)),
                status='scheduled'
            )
            self.stdout.write(f"Flight {origin_code} -> {dest_code} created")

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
