# NJFU-CourseSelector

### 使用教程

#### 准备工作
i.安装python和一款编译器，配置完成后在编译器新建项目\
ii.把文件放入项目文件夹\
iii.安装第三方模块

```p
   pip install pyqt5
   pip install requests
```
#### 启动抢课
i.在抢课时间前半个小时登录教务系统(配合校园VPN食用更佳)，点击F12查询cookie\
ii.在抢课工具设置页填入cookie以及其他信息\
iii.进入抢课页点击启动，到达抢课时间后会自动发送请求，得到课程列表，选择你需要的课程点击确定

#### 注意事项
i.在到达抢课时间之前，启动按钮建议只点击一次\
ii.当前版本的信息输出框还没有实际用处，请在编译器控制台查看输出信息
