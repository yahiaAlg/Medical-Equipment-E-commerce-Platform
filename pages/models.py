from django.db import models

class ContactMessage(models.Model):
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Support'),
        ('partnership', 'Partnership'),
        ('complaint', 'Complaint'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class FAQ(models.Model):
    CATEGORIES = [
        ('ordering', 'Ordering'),
        ('shipping', 'Shipping'),
        ('technical', 'Technical Support'),
        ('warranty', 'Warranties'),
        ('returns', 'Returns & Exchanges'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORIES)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company}"