# coding=utf-8
from django.contrib.auth.models import User, Group, AbstractBaseUser, \
    AbstractUser

from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from adminlte.constants import UsableStatus


class BaseModel(models.Model):
    creator = models.ForeignKey(User, verbose_name=u"数据创建人",
                                null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=u"数据创建时间",
                                      auto_now_add=True, null=True,
                                      blank=True)
    deleted_at = models.DateTimeField(verbose_name=u"数据删除时间",
                                      null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name=u"数据更新时间",
                                      auto_now=True, null=True,
                                      blank=True)

    class Meta:
        abstract = True


class SystemConfig(MPTTModel, BaseModel, UsableStatus):
    name = models.CharField(u"配置名称(英文)", max_length=255, unique=True)
    title = models.CharField(u"配置名称(中文)", max_length=255)
    value = models.CharField(u"配置值", max_length=255)
    parent = TreeForeignKey('self', verbose_name=u'父配置项',
                            null=True, blank=True,
                            related_name='children', db_index=True)

    def __unicode__(self):
        return u"<系统配置-%s-%s>" % (self.name, self.value)

    class Meta:
        verbose_name_plural = verbose_name = u"系统配置"

    class MPTTMeta:
        order_insertion_by = ['name']

    class Config:
        list_template_name = 'adminlte/systemconfig_list.html'
        list_display_fields = ('name', 'parent', 'title', 'value', 'id',)
        list_form_fields = ('parent', 'name', 'title', 'value', 'id',)
        search_fields = ('name', 'title', 'value')


class Menu(MPTTModel, BaseModel, UsableStatus):
    name = models.CharField(u'菜单名称', max_length=50, unique=True)
    icon = models.CharField(u'菜单图标', max_length=50, default='fa-circle-o',
                            help_text=u'参考:http://fontawesome.io')
    parent = TreeForeignKey('self', verbose_name=u'上级菜单',
                            null=True, blank=True,
                            related_name='children', db_index=True)
    app_name = models.CharField(u'App名称', max_length=200,
                                null=True, blank=True, )
    model_name = models.CharField(u'Model名称', max_length=200,
                                  null=True, blank=True,
                                  help_text=u'注意大小写')
    url = models.CharField(u'全路径', max_length=200,
                           null=True, blank=True,
                           help_text=u'选填')
    order = models.PositiveSmallIntegerField(u'排序', default=0)
    status = models.PositiveSmallIntegerField(
        u'状态', choices=UsableStatus.USABLE_STATUS,
        default=UsableStatus.USABLE
    )

    def __unicode__(self):
        return u'<菜单-%s-%s>' % (self.name, self.order)

    class Meta:
        verbose_name_plural = verbose_name = u'菜单'
        ordering = ('order', )

    class MPTTMeta:
        order_insertion_by = ['order']

    class Config:
        list_display_fields = ('name', 'app_name',
                               'model_name', 'url', 'icon', 'order', 'id')
        list_form_fields = ('parent',) + list_display_fields
        search_fields = ('name', 'app_name', 'model_name', 'icon')


class Resource(BaseModel):
    name = models.CharField(u'资源名称', max_length=50)
    app_name = models.CharField(u'所属应用', max_length=200,
                                null=True, blank=True, )
    model_name = models.CharField(u'所属模型', max_length=200,
                                  null=True, blank=True)
    url = models.CharField(u'资源地址', max_length=500,
                           null=True, blank=True,
                           help_text=u'API地址')
    note = models.CharField(u'备注', max_length=500,
                            null=True, blank=True)

    def __unicode__(self):
        return u'<API资源-%s-%s>' % (self.pk, self.name)

    class Meta:
        verbose_name_plural = verbose_name = u'API资源'

    class Config:
        list_display_fields = ('name', 'app_name', 'model_name', 'url', 'id')
        list_form_fields = list_display_fields


class LteUser(User):
    class Meta:
        proxy = True
        app_label = 'adminlte'
        verbose_name_plural = verbose_name = u'用户'

    class Config:
        list_display_fields = ('username', 'groups', 'email',
                               'is_active', 'last_login', 'id', )
        list_form_fields = ('username', 'password',
                            'password',
                            'groups', 'email', 'is_active', 'id',)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.set_password(self.password)
        return super(LteUser, self).save(force_insert=False,
                                         force_update=False,
                                         using=None, update_fields=None)

class LteGroup(Group):
    class Meta:
        proxy = True
        app_label = "adminlte"
        verbose_name_plural = verbose_name = u'角色'

    class Config:
        list_display_fields = ('name', 'id', )
        list_form_fields = list_display_fields


class Permission(BaseModel):
    group = models.ForeignKey(LteGroup, verbose_name=u'角色',
                              related_name='group_permission')
    menus = models.ManyToManyField(Menu, verbose_name=u'菜单',
                                   blank=True)
    resources = models.ManyToManyField(Resource, verbose_name=u'资源',
                                       blank=True)

    def __unicode__(self):
        return self.group.name

    class Meta:
        verbose_name_plural = verbose_name = u'权限'

    class Config:
        list_display_fields = ('group', 'menus', 'resources', 'id')
        list_form_fields = list_display_fields
