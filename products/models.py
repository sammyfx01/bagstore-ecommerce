# products/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('product_list')}?category={self.slug}"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Original price, for showing a discount strike-through"
    )
    stock = models.PositiveIntegerField(default=0, help_text="Used only if this product has no variants")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=300, blank=True, help_text="SEO meta description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def in_stock(self):
        if self.has_variants:
            return self.variants.filter(stock__gt=0).exists()
        return self.stock > 0

    @property
    def is_on_sale(self):
        return self.compare_at_price is not None and self.compare_at_price > self.price

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg or 0, 1)

    @property
    def reviews_count(self):
        return self.reviews.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="e.g. 'Red / Large'")
    sku = models.CharField(max_length=50, blank=True, unique=True, null=True)
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Leave blank to use the product's base price"
    )
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} — {self.name}"

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.price


class ProductAttribute(models.Model):
    """e.g. 'Color', 'Size' — lets variants be structured rather than free text if you want that later"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attributes')
    attribute_name = models.CharField(max_length=50)
    attribute_value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"