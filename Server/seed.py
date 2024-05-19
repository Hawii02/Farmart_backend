from app import db, app
from models import Animal, Category

def seed_data():
    with app.app_context():

        print('Deleting existing data...')

        Animal.query.delete()
        Category.query.delete()

        print('Creating categories...')
        categories = [
            Category(name='Poultry'),
            Category(name='Livestock'),
            Category(name='Equines'),
            Category(name='Camelids'),
            Category(name='Apiary'),
            Category(name='Aquatic'),
            Category(name='Exotic'),
            Category(name='Small Mammals')
        ]
        db.session.add_all(categories)
        db.session.commit()

        print('Creating animals...')

        category_mapping = {category.name: category.id for category in Category.query.all()}
        farmer_id = 1

        animals = [
            Animal(type='chicken', breed='Rhode Island Red', price=900, status='Available',
                   description='egg laying chicken',
                   image_url='https://valleyhatchery.com/wp-content/uploads/2021/11/Rhode-Island-Red-Chicks.webp',
                   farmer_id=farmer_id, category_id=category_mapping['Poultry']),
            Animal(type='turkey', breed='Norfolk', price=2000, status='Available',
                   description='plump-breasted traditional breed turkey',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ29k7naaKpvXxIeybQOaQzSFeBVtv5jRUJanCLCJ8kAA&s',
                   farmer_id=farmer_id, category_id=category_mapping['Poultry']),
            Animal(type='geese', breed='African', price=2500, status='Available',
                   description='meat producers and ornamental birds',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdYtODTnvUa2JvEJgET9ZLfSgwsYM5hI4qq_BsLwE4Ng&s',
                   farmer_id=farmer_id, category_id=category_mapping['Poultry']),
            Animal(type='duck', breed='Pekin', price=1800, status='Available',
                   description='snowy white',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhDEDWh2uwwbnUmc4elpCPlwgl5z6svyaOxw&s',
                   farmer_id=farmer_id, category_id=category_mapping['Poultry']),
            Animal(type='sheep', breed='Dorper', price=7000, status='Available',
                   description='weighing in at approximately 60 kilograms',
                   image_url='https://morningchores.com/wp-content/uploads/2020/12/Dorper-sheep-800x534.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Livestock']),
            Animal(type='goat', breed='Boer', price=6000, status='Available',
                   description='white body with a brown head and ears',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2coiHlSTqgXVzXkNWjfUq1FovlCc5GvKnlReLOfzLWA&s',
                   farmer_id=farmer_id, category_id=category_mapping['Livestock']),
            Animal(type='cow', breed='Boran', price=80000, status='Available',
                   description='weighs in at 400 kilograms',
                   image_url='https://delavidaboran.co.za/images/boran/matings/B05-130%20-%20DIVA%20-%202011.12.29.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Livestock']),
            Animal(type='sheep', breed='Merino', price=7500, status='Available',
                   description='adaptable to any weather and has alot of wool',
                   image_url='https://sockwellusa.com/cdn/shop/articles/merino-wool-vs-wool-whats-the-difference-379043.jpg?v=1684814363&width=800',
                   farmer_id=farmer_id, category_id=category_mapping['Livestock']),
            Animal(type='goat', breed='Saanen', price=7000, status='Available',
                   description='heavy milk producers ',
                   image_url='https://www.thehappychickencoop.com/wp-content/uploads/2023/02/saanen-goat.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Livestock']),
            Animal(type='horse', breed='Arabian', price=800000, status='Available',
                   description='matured built brown horse',
                   image_url='https://madbarn.com/wp-content/uploads/2023/04/Arabian-Horse-Breen-Profile.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Equines']),
            Animal(type='horse', breed='friesian', price=1000000, status='Available',
                   description='stunning black stallion, ten years old',
                   image_url='https://cdn.ehorses.media/image/blur/xxldetails/friesian-horses-stallion-7years-16-1-hh-black-dressagehorses-showhorses-breedinghorses-leisurehorses-bad-wurzach_277b9d82-90c9-44cf-9ef4-4ec3633a243e.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Equines']),
            Animal(type='camel', breed='Kharai', price=70000, status='Available',
                   description='adapts highly in coastal region',
                   image_url='https://www.nativebreed.org/wp-content/uploads/2020/05/Kharai-camel-1024x574.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Camelids']),
            Animal(type='camel', breed='Targui', price=740000, status='Available',
                   description='adapts in harsh weather environment',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRraEqDu1ribiin_YIWD5TVpOECZ6msop1Ja1QZybkj6A&s',
                   farmer_id=farmer_id, category_id=category_mapping['Camelids']),
            Animal(type='camel', breed='Dromedary', price=73000, status='Available',
                   description='have only one hump',
                   image_url='https://i0.wp.com/www.laketobias.com/wp-content/uploads/2021/03/Dromedary-camel-1920x1080-copy.jpg?fit=1920%2C1080&ssl=1',
                   farmer_id=farmer_id, category_id=category_mapping['Camelids']),
            Animal(type='bee', breed='carpenter', price=3000, status='Available',
                   description='body length ranging from about half an inch to over an inch (1.3 to 2.5 centimeters)',
                   image_url='https://files.aptuitivcdn.com/Pqnz49oyx5-1775/images/carpenter-bee-identification.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Apiary']),
            Animal(type='bee', breed='honey', price=4000, status='Available',
                   description='plays a crucial role in pollination and honey production',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQPTWHCOppZQHniu_mRgwQPyobgj0jWGgNuGlR32x4Glw&s',
                   farmer_id=farmer_id, category_id=category_mapping['Apiary']),
            Animal(type='bee', breed='bumble', price=5100, status='Available',
                   description='hairy body covered in dense fuzz',
                   image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6rsjpYIrA4_MXqpsc8i2eUqSovmfThiAXOEs0_5Yfow&s',
                   farmer_id=farmer_id, category_id=category_mapping['Apiary']),
            Animal(type='fish', breed='tilapia', price=1000, status='Available',
                   description='fast growing fish can grow upto 10 years',
                   image_url='https://www.feednavigator.com/var/wrbm_gb_food_pharma/storage/images/_aliases/wrbm_large/publications/feed/feednavigator.com/news/r-d/minty-feed-may-boost-tilapia-survival/9359616-1-eng-GB/Minty-feed-may-boost-tilapia-survival.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Aquatic']),
            Animal(type='fish', breed='mudfish', price=950, status='Available',
                   description='covered in thick and scaleless skin',
                   image_url='https://t3.ftcdn.net/jpg/00/03/22/66/360_F_3226621_ufBqi6pLrjFl9WXCi5TTVABCDNsPvn.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Aquatic']),
            Animal(type='fish', breed='salmon', price=5000, status='Available',
                   description='have silver scales and a silvery-white belly',
                   image_url='https://i.ytimg.com/vi/1bUVGUigUIA/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLD2H_n9xkr-262SWroEb4tyMYzPUg',
                   farmer_id=farmer_id, category_id=category_mapping['Aquatic']),
            Animal(type='ostriches', breed='common', price=120000, status='Available',
                   description='has a long neck and a large size body',
                   image_url='https://www.treehugger.com/thmb/RXeq-0l-3gU8i8f7DBbxUYXYXjI=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-521324136-634374426780412bbd2fdb3bb8c0ba2a.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Exotic']),
            Animal(type='parrot', breed='amazon', price=30000, status='Available',
                   description='have a  short square-shaped tails, and vibrant plumage',
                   image_url='https://media-be.chewy.com/wp-content/uploads/amazon-parrot.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Exotic']),
            Animal(type='rabbit', breed='Dutch', price=4000, status='Available',
                   description='has white markings on the front of its face',
                   image_url='https://homeandroost.co.uk/wp-content/uploads/2021/12/D188EFAF-137B-48AD-8E73-097BB23EC40D-1024x778-1.jpeg',
                   farmer_id=farmer_id, category_id=category_mapping['Small Mammals']),
            Animal(type='rabbit', breed='Chinchilla', price=5000, status='Available',
                   description='10 years old',
                   image_url='https://livestockconservancy.org/wp-content/uploads/2022/08/Giant-Chinchilla-Buck-scaled.jpg',
                   farmer_id=farmer_id, category_id=category_mapping['Small Mammals'])
        ]

        db.session.add_all(animals)
        db.session.commit()

        print('Successfully created animals and categories')

if __name__ == '__main__':
    seed_data()
