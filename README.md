# ChinaTelecomMonitor

> 中国电信话费、通话、流量套餐用量查询 API 服务

本项目通过模拟登录中国电信接口，获取手机话费、通话时长、流量使用情况等数据。可部署在服务器、x86软路由等设备上运行，为第三方系统提供数据查询接口。

## 📋 目录

- [特性](#-特性)
- [使用案例](#-使用案例)
- [快速开始](#-快速开始)
  - [Docker 部署](#docker-部署)
- [API 文档](#-api-文档)
- [常见问题](#-常见问题)
- [致谢](#-致谢)

## ✨ 特性

- ✅ **Token 缓存机制** - 本地保存登录 token，有效期内自动复用，避免重复登录
- ✅ **Docker 部署** - 一键部署 API 查询服务
- ✅ **RESTful API** - 提供标准 REST API，方便第三方系统集成
- ✅ **高并发支持** - 支持多线程并发查询，性能稳定
- ✅ **数据持久化** - 登录信息持久化存储，容器重启后数据不丢失

## 🎯 使用案例

- [iOS 自制 UI 面板](https://github.com/Cp0204/ChinaTelecomMonitor/issues/18) - By: LRZ9712
- [HomeAssistant 插件集成](https://bbs.hassbian.com/thread-29129-1-1.html) [CTM电信](https://github.com/hlhk2017/ChinaTelecomMonitor-Homeassistant-Integration) - By: hlhk2017
- [HomeAssistant 中国电信接入视频教程](https://www.bilibili.com/video/BV1F5NLe7EUJ/) - By: 米哟MIO

## 🚀 快速开始

### Docker 部署

本项目提供 Docker 容器化部署方案，方便快速部署和使用。API 服务主要用于第三方系统（如 HomeAssistant 等）获取电信套餐使用信息。

> ⚠️ **安全警告**
> 
> 登录成功后，会在服务器 `config/login_info.db` (SQLite 数据库) 中**记录账号包括 token 在内的敏感信息**。token 长期有效，直到在其他地方登录被挤下线。程序获取数据时会先尝试用已记录的 token 去请求，避免重复发出登录请求。
> 
> **⚠️ 请勿使用他人部署的 API 服务，以免敏感信息外泄 ⚠️**

#### 构建 Docker 镜像

在项目根目录执行以下命令构建镜像（支持跨平台构建，适用于 Mac 构建 x86 镜像）：

```bash
docker build --platform linux/amd64 -t dtzsghnr/chinatelecommonitor:latest .
```

#### 使用 Docker 命令部署

```bash
# 创建本地数据目录（用于持久化数据库和配置）
mkdir -p ./china-telecom-monitor/config

# 运行容器（数据持久化到本地 ./china-telecom-monitor/config 目录）
docker run -d \
  --name china-telecom-monitor \
  -p 10000:10000 \
  -v $(pwd)/china-telecom-monitor/config:/app/config \
  --network bridge \
  --restart unless-stopped \
  dtzsghnr/chinatelecommonitor:latest
```

#### 使用 Docker Compose 部署

创建 `docker-compose.yml` 文件：

```yaml
name: china-telecom-monitor
services:
  china-telecom-monitor:
    image: dtzsghnr/chinatelecommonitor:latest
    container_name: china-telecom-monitor
    network_mode: bridge
    ports:
      - 10000:10000
    volumes:
      # 数据持久化：将容器内的 /app/config 目录挂载到本地
      # 数据库文件 login_info.db 会保存在本地，容器重启后数据不丢失
      - ./china-telecom-monitor/config:/app/config
    restart: unless-stopped
```

然后运行：

```bash
docker-compose up -d
```

#### 数据持久化说明

- 通过 `-v` 参数将容器的 `/app/config` 目录挂载到本地目录
- 数据库文件 `login_info.db` 会保存在本地，容器删除重建后数据不会丢失
- **建议定期备份** `./china-telecom-monitor/config` 目录，包含重要的登录 token 信息


## 📖 API 文档

所有接口均支持 `GET` 和 `POST` 方法，默认端口为 `10000`。

### 接口列表

| 接口路径 | 说明 | 备注 |
| -------- | ---- | ---- |
| `/login` | 登录接口 | 返回用户信息；无需单独请求，其他接口未登录时会自动登录 |
| `/qryImportantData` | 查询主要信息 | 返回话费、通话、流量等总用量信息 |
| `/userFluxPackage` | 查询流量包明细 | 返回详细的流量包使用情况 |
| `/qryShareUsage` | 查询共享套餐 | 返回共享套餐各号码用量 |
| `/summary` | 简化数据接口 | `/qryImportantData` 的简化版本，返回格式化的数据 |

### 请求方式

#### GET 请求示例

```bash
# 使用 URL 参数
curl "http://127.0.0.1:10000/summary?phonenum=18912345678&password=123456"
```

#### POST 请求示例

```bash
curl --request POST \
  --url http://127.0.0.1:10000/summary \
  --header 'Content-Type: application/json' \
  --data '{
    "phonenum": "18912345678",
    "password": "123456"
  }'
```

### 响应格式

#### `/summary` 接口响应示例

```json
{
  "phonenum": "18912345678",
  "balance": 0,
  "voiceUsage": 39,
  "voiceBalance": 2211,
  "voiceTotal": 2250,
  "flowUse": 7366923,
  "flowTotal": 7366923,
  "flowOver": 222222,
  "commonUse": 7273962,
  "commonTotal": 25550446,
  "commonOver": 222222,
  "specialUse": 92961,
  "specialTotal": 215265280,
  "createTime": "2024-05-12 14:13:28",
  "flowItems": [
    {
      "name": "国内通用流量(达量降速)",
      "use": 10241024,
      "balance": 0,
      "total": 10241024
    },
    {
      "name": "国内通用流量(非畅享)",
      "use": 1,
      "balance": 10241023,
      "total": 10241024
    },
    {
      "name": "专用流量",
      "use": 1,
      "balance": 10241023,
      "total": 10241024
    }
  ]
}
```

#### 字段说明

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `phonenum` | string | 手机号码 |
| `balance` | number | 账户余额（单位：分） |
| `voiceUsage` | number | 语音通话已使用时长（单位：分钟） |
| `voiceBalance` | number | 语音通话剩余时长（单位：分钟） |
| `voiceTotal` | number | 语音通话总时长（单位：分钟） |
| `flowUse` | number | 总流量已使用量（单位：KB） |
| `flowTotal` | number | 总流量总量（单位：KB） |
| `flowOver` | number | 总流量超量（单位：KB） |
| `commonUse` | number | 通用流量已使用量（单位：KB） |
| `commonTotal` | number | 通用流量总量（单位：KB） |
| `commonOver` | number | 通用流量超量（单位：KB） |
| `specialUse` | number | 专用流量已使用量（单位：KB） |
| `specialTotal` | number | 专用流量总量（单位：KB） |
| `createTime` | string | 数据创建时间 |
| `flowItems` | array | 流量类型列表，包含各流量包的详细信息 |

## ❓ 常见问题

### 1. 登录失败怎么办？

- 检查手机号和密码是否正确
- 确认账号未被其他设备登录（会被挤下线）
- 如果 token 过期，程序会自动重新登录

### 2. 如何查看数据库中的登录信息？

可以使用项目提供的 `view_db.py` 脚本查看：

```bash
python view_db.py
```

### 3. 数据持久化在哪里？

数据保存在 `./china-telecom-monitor/config/login_info.db` 文件中，包含登录 token 等敏感信息，请妥善保管。

### 4. 支持多账号吗？

支持。每个账号的登录信息会分别存储在数据库中，通过 `phonenum` 参数区分。

## 🙏 致谢

本项目大量参考其他项目的代码，在此表示感谢！

- [ChinaTelecomMonitor](https://github.com/LambdaExpression/ChinaTelecomMonitor) - Go 语言实现版本
- [boxjs](https://github.com/gsons/boxjs) - 感谢开源提供的电信接口
## 免责声明

本仓库或本仓库相关的仓库, 以下简称为本仓库.
本仓库或本仓库相关的仓库的管理者, 以下简称为本仓库管理者.
本仓库或本仓库相关的仓库的任何人员, 以下简称为本仓库人员.
本仓库或本仓库相关的仓库内分享的任何内容, 以下简称为本仓库内容.

本仓库内容，仅用于测试和学习研究，禁止用于商业用途，不得将其用于违反国家/地区/组织等的法律法规或相关规定的其他用途. 本仓库人员均不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断. 禁止任何公众号、自媒体进行任何形式的转载、发布.

本仓库内容的域名地址信息可以被任何人通过开发人员工具获取，没有经过逆向工程或网络攻击，不构成入侵计算机系统

本仓库人员对任何本仓库内容问题概不负责，包括但不限于由任何本仓库内容错误导致的任何损失或损害.

间接使用本仓库内容的任何用户，包括但不限于建立 VPS 或在某些行为违反国家/地区法律或相关法规的情况下进行传播, 本仓库人员对于由此引起的任何隐私泄漏或其他后果概不负责.

请勿将本仓库内容用于商业或非法目的，否则后果自负.

如果任何单位或个人认为本仓库内容可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，本仓库管理者将在收到认证文件后删除相关本仓库内容.

任何以任何方式查看本仓库内容的人或直接或间接使用本仓库内容的使用者都应仔细阅读此声明。本仓库管理者保留随时更改或补充此免责声明的权利。一旦使用/复制/修改了本仓库内容，则视为您已接受此免责声明.

本仓库内容中涉及的第三方硬件、软件等，与本仓库内容没有任何直接或间接的关系。本仓库内容仅对部署和使用过程进行客观描述，不代表支持使用任何第三方硬件、软件。使用任何第三方硬件、软件，所造成的一切后果由使用的个人或组织承担，与本仓库内容无关。

所有基于本仓库内容的源代码，进行的任何修改，为其他个人或组织的自发行为，与本仓库内容没有任何直接或间接的关系，所造成的一切后果亦与本仓库内容和本仓库人员无关。

本仓库管理者保留随时对免责声明进行补充或更改的权利，直接或间接使用本仓库内容的个人或组织，视为接受本仓库分享的内容的免责声明。

请不要在中华人民共和国境内使用本仓库内容。

所有直接或间接使用本仓库内容的个人和组织，应 24 小时内完成学习和研究，并及时删除本仓库内容。如对本仓库内容的功能有需求，应自行开发相关功能。

您必须在下载后的 24 小时内从您以任何形式存放或使用本仓库内容的任何硬件/软件/介质中完全删除本仓库内容.

您以任何形式阅读/使用/复制/修改了本仓库内容，则视为已接受此免责声明，请仔细阅读