# jiango
Django 框架的功能扩展

目前基于 Django 1.4 的原因是因为比较稳定的版本。后期版本 Django 变化较多并且是为 python 2.6/3.x 双向兼容设计的，冗余代码太多。
等到 Django 出了 2.0 再考虑升级兼容。

## 已有模块
* **admin** 管理后台框架，简单的用户管理，权限管理，日志记录
* **api** API 开发工具，方便快速的制定 API 接口
* **bootstrap** Bootstrap 2、3 表单支持
* **captcha** 不需要使用 SESSION、Cookie 的验证码系统
* **cms** 简单的内容管理系统，待完善模版功能
* **debug** 简单的调试信息输出
* **forms** 表单扩展
* **middleware.mobile** 移动端识别
* **pagination** 分页插件
* **serializers** 序列化，主要用于 API 系统
* **templatetags.form** 表单字段自定义属性
* **templatetags.humanize** 人性化信息显示


## 如何使用
可以直接下载 https://github.com/yefei/jiango-blank 代码，这是一个空项目
