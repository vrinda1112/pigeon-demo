import uuid as uuid

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

product_type_injection_choices = (
    ('FO011', 'N-S'),
    ('FO012', 'N-M'),
    ('FO013', 'N-L'),
    ('FO014', 'N-Y')  # injection status based on nipple size
)
lim_checksheet_status_choices = (
    ('ABNORMAL', 'ABNORMAL'),
    ('NORMAL', 'NORMAL')
)
lim_valve_status = (
    ('OPEN', 'OPEN'),
    ('CLOSE', 'CLOSE')
)
shift = (
    ('A', 'MORNING'),
    ('B', 'AFTERNOON'),
    ('C', 'NIGHT')
)

user_roles = (
    ('LO','LIM-OPERATOR'),
    ('PO','PRINT-OPERATOR'),
    ('PM','PROCESS-MANAGER'),
    ('SI','SHIFT-INCHARGE'),
)

class UserProfile(models.Model):
    """
    user.is_superuser ==> Full Access (is_superuser and is_staff)
    user.is_staff ==> Access Based on Permission (is_staff)
    For staff/super user is_staff will always be True

    nor superuser nor staff but => Views allowed to Customer (view/download)

    nor superuser nor staff but is_cpcb => Views allowed to CPCB (view/download)

    """
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=user_roles,default=None)
    email = models.EmailField(max_length=60, default=None, null=True,
        unique=True)
    name = models.CharField(max_length=60, null=False, verbose_name='Name')
    phone = models.CharField(max_length=10, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True,
        verbose_name='Created On')
    last_login = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return '%s' % (self.email or self.user)

    @staticmethod
    def new_user_hook(sender, instance, created, **kwargs):
        """
        A User post_save hook to create a User Profile
        """
        if created and instance.username != settings.ANONYMOUS_USER_NAME:
            profile = UserProfile.objects.create(user=instance)
            profile.user = instance
            profile.email = instance.email
            profile.name = instance.username
            profile.save()


class LIMChecklist(models.Model):
    machine_number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    product_type = models.CharField(max_length=20,
        choices=product_type_injection_choices, )

    shift = models.CharField(choices=shift,max_length=20)
    reporter = models.ForeignKey(UserProfile, on_delete=models.PROTECT,
        related_name='%(class)s_reported_by')# in
    # case the user leaves org, and deleted the lim entries should not be
    # deleted
    cw_temp = models.SmallIntegerField(blank=True, null=True,
        help_text="lim cylinder water temperature,usually 25-40 C")
    water_pressure = models.SmallIntegerField(blank=True, null=True,
        help_text="pressure of water in lim, usually 2-4.5 bar")
    oil_temp = models.SmallIntegerField(blank=True, null=True,
        help_text="hydraulic oil temperature, usually 40-50 C")
    leak_check = models.BooleanField(blank=True, null=True,
        help_text="any leakage in material wires")
    lubrication_check = models.CharField(blank=True, null=True,max_length=120,
        choices=lim_checksheet_status_choices,
        help_text="lubrication of wires"),
    silicon_feeder = models.CharField(blank=True, null=True,max_length=120,
        choices=lim_checksheet_status_choices,
        help_text="silicon raw material feeder system")
    heater_temp = models.CharField(blank=True, null=True,max_length=120,
        choices=lim_checksheet_status_choices,
        help_text="heater temperature")
    oil_level = models.CharField(blank=True, null=True,max_length=120,
        choices=lim_checksheet_status_choices, help_text="hydraulic oil level")
    oil_leakage = models.BooleanField(blank=True, null=True,
        help_text="Oil leakage from or of any joints")
    feeder_pressure = models.SmallIntegerField(blank=True, null=True,
        help_text="Pressure from which raw material is pushed to feeder")
    desk_light = models.CharField(blank=True, null=True,max_length=120,
        choices=lim_checksheet_status_choices)
    conveyor = models.CharField(blank=True, null=True,
        choices=lim_checksheet_status_choices,
        max_length=120,
        help_text="check product rolling down the line")
    valve_A = models.CharField(blank=True, null=True,max_length=120, choices=lim_valve_status)
    valve_B = models.CharField(blank=True, null=True, max_length=120,choices=lim_valve_status)
    air_pressure = models.SmallIntegerField(blank=True, null=True,
        help_text="usually 2-6 bar")
    purge_status = models.BooleanField(blank=True, null=True,
        help_text="purge material removed from machine")
    cleaning_status = models.BooleanField(blank=True, null=True)


class LIMParameters(models.Model):
    machine_number = models.IntegerField()
    reporter = models.ForeignKey(UserProfile, on_delete=models.PROTECT,related_name='%(class)s_reported_by')

    created = models.DateTimeField(auto_now_add=True)
    shift = models.CharField(choices=shift,max_length=120)
    clamping_force = models.SmallIntegerField(blank=True,
        help_text="force required to close the mold")
    injection_time = models.SmallIntegerField(blank=True,
        help_text="time taken to inject raw material in mold in secs")
    holding_time = models.SmallIntegerField(blank=True,
        help_text="mateial holded in mold in secs")
    cooling_time = models.SmallIntegerField(blank=True,
        help_text="time taken for product to take shape")
    cycle_time = models.SmallIntegerField(blank=True,
        help_text="time taken from first opening of mold to next")
    product_type = models.CharField(choices=product_type_injection_choices,
        help_text="size of nipple or bottle", max_length=120)
    material_lot_no = models.CharField(blank=False, max_length=120,
        help_text="raw material lot no")
    cavity_no = models.SmallIntegerField(blank=True,
        help_text="1-8 , no of cavities in lin from where nipples come out")
    air_pressure = models.SmallIntegerField(blank=True,
        help_text="pressure with which nipples are ejected in bar")
    feed_stock_pressure = models.IntegerField(blank=True,
        help_text="material feeding pressure")


class ProductionSheetLIM(models.Model):
    machine_number = models.IntegerField()
    product_type = models.CharField(choices=product_type_injection_choices,max_length=20)
    reporter = models.ForeignKey(UserProfile, on_delete=models.PROTECT,
        related_name='%(class)s_reported_by')

    total_shots = models.IntegerField(blank=True, null=False)
    created = models.DateTimeField(auto_now_add=True)
    shift = models.CharField(choices=shift,max_length=20)
    shot_weight = models.IntegerField(blank=True, help_text="1 shot=8 nipples")
    rm_code = models.CharField(max_length=120,blank=False,
        help_text="raw material code")
    rm_lot_no = models.CharField(blank=False, max_length=120,
        help_text="raw materail manufacturing lot no")
    bin_number = models.CharField(max_length=120, blank=False)
    product_weight = models.IntegerField(blank=True,
        help_text="total weight of produts produced")
    lot_no = models.CharField(max_length=120,
        help_text="unique alpha numeric string used by pigeon officials")


class LIMProductionCounters(models.Model):
    # before ending shift , the operator had to fill this
    machine_number = models.IntegerField()
    product_type = models.CharField(choices=product_type_injection_choices,max_length=120)
    reporter = models.ForeignKey(UserProfile, on_delete=models.PROTECT,
        related_name='%(class)s_reported_by')
    counter_start = models.IntegerField(blank=True,
        help_text="Total no.of products at the time of starting shift")
    counter_end = models.IntegerField(blank=True,
        help_text="Total products produced at the end of shift")
    created = models.DateTimeField(auto_now_add=True)
    setup_rejection = models.IntegerField(blank=True,
        help_text="rejected bottles due to setting up of LIM in cases of downtime")
    total_line_rejection = models.IntegerField(blank=True)
    qc_samples_taken = models.IntegerField(blank=True, null=True)
    qc_samples_ok = models.IntegerField(blank=True)





































