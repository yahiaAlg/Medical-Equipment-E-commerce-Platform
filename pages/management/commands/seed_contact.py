from django.core.management.base import BaseCommand
from ...models import ContactMessage, FAQ, Testimonial, SiteInformation


class Command(BaseCommand):
    help = "Seeds contact messages, FAQs, testimonials, and site information"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding contact data...")

        # Create or update Site Information
        site_info = SiteInformation.get_instance()
        site_info.company_name = "Fennec Med"
        site_info.tva_rate = 0.05
        site_info.tagline = "Providing quality medical materials to families across the region since 2022"
        site_info.phone = "03 9591 5378"
        site_info.fax = "03 7068 5073"
        site_info.email = "admin@newbaymedical.com.au"
        site_info.address = "59 Bay St, Brighton VIC 3186"
        site_info.facebook_url = "#"
        site_info.instagram_url = "#"
        site_info.whatsapp_url = "#"
        site_info.youtube_url = "#"
        site_info.about_text = """We believe that obtaining medical supplies should be both easy and reliable. 
        From the moment you reach out to us, you'll experience a seamless process with a warm and supportive team. 
        Our commitment to excellence means that we're constantly evolving, ensuring you receive the best products 
        and service possible."""
        site_info.save()
        self.stdout.write("Created/Updated site information")

        # Create FAQs
        faqs_data = [
            {
                "category": "ordering",
                "question": "How do I place a bulk order?",
                "answer": "You can place bulk orders directly through our website. Add products to cart and quantities of 10+ automatically receive bulk pricing discounts. For orders over $10,000, contact our sales team for additional discounts.",
                "order": 1,
            },
            {
                "category": "ordering",
                "question": "Do you offer leasing options?",
                "answer": "Yes, we offer flexible leasing options for equipment purchases. Contact our financing department to discuss terms and requirements.",
                "order": 2,
            },
            {
                "category": "shipping",
                "question": "What are your shipping times?",
                "answer": "Standard shipping takes 5-7 business days. Expedited shipping (2-3 days) and next-day delivery are available for urgent orders.",
                "order": 1,
            },
            {
                "category": "shipping",
                "question": "Do you ship internationally?",
                "answer": "Yes, we ship to most countries worldwide. International shipping times vary by destination, typically 10-15 business days.",
                "order": 2,
            },
            {
                "category": "technical",
                "question": "Do your products come with installation support?",
                "answer": "All major equipment includes installation guides. Professional installation services are available for an additional fee.",
                "order": 1,
            },
            {
                "category": "technical",
                "question": "What kind of training do you provide?",
                "answer": "We offer comprehensive training programs including online tutorials, in-person training, and ongoing technical support.",
                "order": 2,
            },
            {
                "category": "warranty",
                "question": "What is covered under warranty?",
                "answer": "Our warranty covers manufacturing defects and equipment failures under normal use. Extended warranty options are available.",
                "order": 1,
            },
            {
                "category": "warranty",
                "question": "How do I claim warranty service?",
                "answer": "Contact our support team with your order number and issue description. We will arrange repair or replacement as appropriate.",
                "order": 2,
            },
            {
                "category": "returns",
                "question": "What is your return policy?",
                "answer": "30-day return policy on most items. Equipment must be unused and in original packaging. Custom orders are non-returnable.",
                "order": 1,
            },
            {
                "category": "returns",
                "question": "How do I initiate a return?",
                "answer": "Contact customer service to receive a return authorization number. Ship the item back with all original packaging and documentation.",
                "order": 2,
            },
        ]

        for faq_data in faqs_data:
            FAQ.objects.get_or_create(question=faq_data["question"], defaults=faq_data)

        self.stdout.write(f"Created {len(faqs_data)} FAQs")

        # Create Testimonials
        testimonials_data = [
            {
                "name": "John Doe",
                "position": "Customer",
                "company": "",
                "content": "The products are of high quality and the service is excellent. Highly recommend!",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Jane Smith",
                "position": "Customer",
                "company": "",
                "content": "Great experience with Fennec Med. The staff is very knowledgeable and helpful.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Robert Johnson",
                "position": "Customer",
                "company": "",
                "content": "I've been using their medical supplies for years and have always been satisfied.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Dr. Robert Martinez",
                "position": "Chief of Cardiology",
                "company": "Metro General Hospital",
                "content": "Outstanding quality equipment and exceptional customer service. The diagnostic tools have significantly improved our patient care capabilities.",
                "rating": 5,
                "is_featured": False,
            },
            {
                "name": "Lisa Thompson",
                "position": "Pharmacy Manager",
                "company": "HealthPlus Pharmacy Chain",
                "content": "We have been ordering from this supplier for over 3 years. Reliable, competitive pricing, and fast delivery every time.",
                "rating": 5,
                "is_featured": False,
            },
        ]

        for test_data in testimonials_data:
            Testimonial.objects.get_or_create(
                name=test_data["name"], defaults=test_data
            )

        self.stdout.write(f"Created {len(testimonials_data)} testimonials")

        # Create sample contact messages
        messages_data = [
            {
                "name": "John Smith",
                "email": "john.smith@hospital.com",
                "phone": "+1-555-0101",
                "inquiry_type": "general",
                "subject": "Interested in bulk pricing",
                "message": "We are looking to purchase diagnostic equipment for our new wing. Could you provide information on bulk discounts?",
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.j@clinic.com",
                "phone": "+1-555-0102",
                "inquiry_type": "technical",
                "subject": "Equipment installation question",
                "message": "Do you provide installation services for the ultrasound machines? What are the requirements?",
            },
            {
                "name": "David Lee",
                "email": "dlee@pharmacy.com",
                "inquiry_type": "partnership",
                "subject": "Partnership opportunity",
                "message": "Our pharmacy chain is interested in establishing a long-term partnership. Please contact us to discuss.",
            },
        ]

        for msg_data in messages_data:
            ContactMessage.objects.get_or_create(
                email=msg_data["email"], subject=msg_data["subject"], defaults=msg_data
            )

        self.stdout.write(f"Created {len(messages_data)} contact messages")
        self.stdout.write(self.style.SUCCESS("Successfully seeded contact data!"))
