import unittest
from sqlalchemy.exc import IntegrityError
from project import db, app
from project.customers.models import Customer


class TestCustomerModel(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_customer_creation(self):
        customer = Customer(name='John Doe', city='Warsaw', age=30, pesel='12345678901', street='Main St', appNo='A123')
        db.session.add(customer)
        db.session.commit()
        self.assertIsNotNone(customer.id)

    def test_invalid_age(self):
        customer = Customer(name='Jane Doe', city='Krakow', age=-5, pesel='98765432101', street='Side St', appNo='B456')
        db.session.add(customer)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_sql_injection(self):
        customer = Customer(name="Robert'); DROP TABLE customers;--", city='Lodz', age=25, pesel='11111111111',
                            street='Hacker St', appNo='H4X0R')
        db.session.add(customer)
        db.session.commit()
        self.assertNotIn("DROP TABLE", customer.name)

    def test_javascript_injection(self):
        customer = Customer(name='<script>alert("XSS")</script>', city='Poznan', age=22, pesel='55555555555',
                            street='Script St', appNo='JS666')
        db.session.add(customer)
        db.session.commit()
        self.assertNotIn('<script>', customer.name)
        self.assertNotIn('</script>', customer.name)

    def test_extreme_string_length(self):
        long_name = 'X' * 300
        customer = Customer(name=long_name, city='Gdansk', age=40, pesel='44444444444', street='Long St',
                            appNo='EXT999')
        db.session.add(customer)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_empty_fields(self):
        test_cases = [
            {'name': '', 'city': '', 'age': 0, 'pesel': '', 'street': '', 'appNo': ''},
            {'name': None, 'city': None, 'age': None, 'pesel': None, 'street': None, 'appNo': None}
        ]

        for case in test_cases:
            with self.subTest(case=case):
                customer = Customer(
                    name=case['name'],
                    city=case['city'],
                    age=case['age'],
                    pesel=case['pesel'],
                    street=case['street'],
                    appNo=case['appNo']
                )
                db.session.add(customer)
                with self.assertRaises(IntegrityError):
                    db.session.commit()

    def test_unique_pesel(self):
        customer1 = Customer(name='Anna Kowalska', city='Wroclaw', age=28, pesel='66666666666', street='Test St',
                             appNo='C001')
        customer2 = Customer(name='Pawel Nowak', city='Lublin', age=35, pesel='66666666666', street='Test St',
                             appNo='C002')
        db.session.add(customer1)
        db.session.commit()
        db.session.add(customer2)
        with self.assertRaises(IntegrityError):
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
