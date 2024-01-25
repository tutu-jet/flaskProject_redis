# 构建阶段
# 指定了使用Python 3.9作为构建阶段的基础镜像，并且给这个阶段起了一个名字叫做builder。
FROM python:3.9 AS builder

# 设置工作目录
# 设置了工作目录为/app，这是在容器中的一个目录，用于存放应用程序的文件。
WORKDIR /app

# 复制应用程序文件到容器中
# 将当前目录中的所有文件复制到容器的/app目录中，这样就将应用程序的所有文件都复制到了容器中。
COPY . .

# 安装依赖
# 安装了我们自定义的应用程序的依赖，requirements.txt文件列出了所有需要安装的Python依赖包。
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
# 指定了容器将会监听的端口号，这里是5000端口。
EXPOSE 5000

# 设置容器启动命令
# 设置了容器启动时执行的命令，这里是运行app.py文件，启动Python应用程序。
CMD ["python", "app.py"]
