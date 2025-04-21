# FastAPIX

## 项目概述

FastAPIX 是一个基于 FastAPI 框架的高性能、扩展性强的 Web 应用开发模板，专为现代化 Python Web 服务开发而设计。项目采用依赖注入、清晰的模块化结构和数据库优先的工作流，帮助开发团队快速构建高质量的 RESTful API 服务。

### 主要功能

* 完整的用户认证与授权系统
  * 基于JWT的访问令牌和刷新令牌
  * 支持Redis或内存存储令牌（可配置）
  * 支持令牌吊销和多端登录控制
  * 可自定义令牌类型和有效期
* 模块化的项目结构，便于团队协作与扩展
* 内置数据库 ORM 支持 (SQLAlchemy)
* Redis 缓存集成
* 全面的 API 文档 (基于 Swagger/OpenAPI)
* 依赖注入系统，提高代码可测试性和可维护性
* SQL 优先的开发工作流，充分利用数据库特性

## 设计原则与架构

FastAPIX 严格遵循 SOLID 原则和现代软件设计模式，以构建健壮、可维护和可扩展的 API 服务。

### SOLID 原则实践

1. **单一职责原则 (SRP)**
   - 每个模块和类只负责一个特定功能
   - 例如，用户管理被分为模型、仓库、服务和路由四个不同组件，各司其职

2. **开放封闭原则 (OCP)**
   - 系统设计允许通过扩展而非修改来添加新功能
   - 通过抽象接口和依赖注入实现功能扩展

3. **里氏替换原则 (LSP)**
   - 确保子类可以替换其父类而不影响程序正确性
   - 所有接口实现保持一致的行为约定

4. **接口隔离原则 (ISP)**
   - API 设计提供精确的、粒度合适的接口
   - 避免强制客户端依赖于它们不使用的方法

5. **依赖倒置原则 (DIP)**
   - 高层模块不依赖于低层模块，两者都依赖于抽象
   - 通过依赖注入系统实现松耦合设计

### 核心架构模式

FastAPIX 采用分层架构，清晰分离关注点：

#### 数据访问对象 (DAO) / 仓库模式

**用户仓库示例：**
```python
class UserRepository:
    """负责所有与用户相关的数据库操作"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db_session.query(User).filter(User.id == user_id).first()
    
    def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
```

**优势：**
- 数据访问逻辑封装，便于数据源切换
- 提高代码可重用性
- 简化单元测试，支持模拟数据
- 集中管理持久化逻辑，提高可维护性

#### 服务层模式

**用户服务示例：**
```python
class UserService:
    """包含所有用户相关业务逻辑"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    def create_user(self, user_data: UserCreate) -> User:
        # 业务逻辑：检查用户是否已存在
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
            
        # 业务逻辑：密码哈希处理
        hashed_password = get_password_hash(user_data.password)
        user_data_dict = user_data.dict()
        user_data_dict["password"] = hashed_password
        
        return self.user_repository.create(UserCreate(**user_data_dict))
```

**优势：**
- 业务逻辑集中管理，消除重复
- 提高可测试性，便于编写单元测试
- 实现表现层与数据访问层解耦
- 增强灵活性和可扩展性

#### 依赖注入模式

FastAPIX采用模块化的依赖注入设计,每个功能模块管理自己的依赖:

**模块级依赖定义 (apps/users/dependencies.py):**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from engines import AsyncDBSession
from apps.users.repository import UserRepository
from apps.users.service import UserService

def get_user_service(db: AsyncSession = Depends(AsyncDBSession)) -> UserService:
    """获取用户服务实例"""
    user_repository = UserRepository(db)
    return UserService(user_repository)
```

**处理器实现 (apps/users/handlers.py):**
```python
from fastapi import Depends
from apps.users.schemas import UserCreate, UserResponse
from apps.users.service import UserService
from apps.users.dependencies import get_user_service
from utils.response import APIResponse

async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """创建新用户的处理函数"""
    created_user = await user_service.create_user(user_data)
    return APIResponse.success(data=created_user, msg="用户创建成功")
```

**在API路由中注册处理器 (apps/users/router.py):**
```python
from fastapi import APIRouter
from apps.users.schemas import UserResponse
from apps.users.handlers import create_user

router = APIRouter()

router.add_api_route(
    "/",
    endpoint=create_user,
    methods=["POST"],
    response_model=UserResponse,
    summary="创建新用户"
)
```

**优势:**
- 模块化封装 - 每个模块管理自己的依赖
- 松耦合设计 - 通过依赖注入实现组件解耦
- 简化测试 - 便于在测试中替换依赖
- 代码复用 - 减少重复的依赖创建逻辑

### 数据处理流程图

为了更直观地理解FastAPIX的架构和数据流转过程，以下是一个完整的数据处理流程图：

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│                │      │                │      │                │
│   HTTP请求     │──────▶    路由层      │──────▶    处理器层     │
│   (Request)    │      │   (Router)     │      │   (Handler)    │
│                │      │                │      │                │
└────────────────┘      └────────────────┘      └────────────────┘
                                                        │
                                                        │ 依赖注入
                                                        ▼
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│                │      │                │      │                │
│    HTTP响应    │◀─────│    响应格式化   │◀─────│    服务层      │
│   (Response)   │      │   (Response)   │      │   (Service)    │
│                │      │                │      │                │
└────────────────┘      └────────────────┘      └────────────────┘
                                                        │
                                                        │ 调用
                                                        ▼
                                               ┌────────────────┐
                                               │                │
                                               │    仓库层      │
                                               │  (Repository)  │
                                               │                │
                                               └────────────────┘
                                                        │
                                                        │ 操作
                                                        ▼
                                               ┌────────────────┐
                                               │                │
                                               │    数据库      │
                                               │   (Database)   │
                                               │                │
                                               └────────────────┘
```

**数据流处理说明：**

1. **请求接收**：HTTP请求进入系统，由FastAPI框架解析请求数据
2. **路由分发**：路由层(Router)负责将请求分发到对应的处理器
3. **请求处理**：处理器层(Handler)接收请求，并依赖注入相关服务
4. **业务处理**：服务层(Service)包含所有业务逻辑，执行核心处理
5. **数据访问**：仓库层(Repository)提供数据访问接口，处理与数据库交互（多个模块可共享同一数据模型）
6. **数据持久化**：数据库层存储或检索数据，令牌根据配置存储在Redis或内存中
7. **响应构建**：数据经过服务层处理后，由APIResponse格式化
8. **响应返回**：将格式化后的响应返回给客户端

每一层都有明确的职责和边界，通过依赖注入实现松耦合，使系统更加灵活、可维护和可测试。

## 开发理念

FastAPIX 采用"数据库优先"的开发方法，这种方法有以下优势：

1. **开发效率高**：直接从现有数据库或 SQL 脚本生成模型，避免从模型到数据库的反向工程
2. **专注于数据库设计**：充分利用 SQL 专业知识进行数据库优化
3. **快速迭代**：修改数据库后可以迅速重新生成模型，减少模型和数据库不同步的风险
4. **SQL 的精确控制**：对索引、约束、存储过程等有更精确的控制

### Redis数据库分配策略

FastAPIX 采用多数据库策略使用 Redis，每个功能使用独立的数据库，提高隔离性和性能：

- **DB 0**: 默认数据库（通常用于测试）
- **DB 1**: 通用缓存
- **DB 2**: 会话存储  
- **DB 3**: 速率限制
- **DB 4**: 任务队列

Redis客户端设计允许在每次操作时指定数据库，而不是在全局配置中固定，提高了灵活性和扩展性。例如：

```python
# 存储缓存数据
redis_client.set("user:profile:1", json.dumps(user_data), expiration=3600, db=settings.REDIS_DB_CACHE)

# 获取会话数据
session_data = redis_client.get(session_id, db=settings.REDIS_DB_SESSION)
```

### 令牌存储策略

FastAPIX 支持两种令牌存储方式，可通过配置文件切换：

1. **Redis存储** (默认)：
   - 访问令牌存储在Redis中，而不是数据库
   - 提高性能 - 频繁的令牌验证操作可以快速完成
   - 简化令牌管理 - 令牌自动过期机制，不需要额外的清理任务
   - 增强安全性 - 可以即时吊销令牌
   - 支持水平扩展 - 多实例之间可以共享令牌信息

2. **内存存储**：
   - 访问令牌存储在应用内存中
   - 无需外部依赖，更容易部署和测试
   - 适用于单实例部署和开发环境
   - 服务重启会导致令牌丢失

通过在配置中设置 `USE_REDIS_FOR_TOKENS=True/False` 来选择存储方式。

## 推荐的工具

* **SQLAlchemy AutoMap**：直接从现有数据库反射生成模型
* **sqlacodegen**：从数据库生成 SQLAlchemy 模型代码

## 本地开发环境要求

* Python 3.10+
* FastAPI 0.112.1+
* SQLAlchemy 2.0+
* Redis 6.0+

## 安装与使用

1. 克隆仓库:
   ```
   git clone https://github.com/tao-xiaoxin/FastAPIX.git
   ```

2. 进入项目目录:
   ```
   cd FastAPIX
   ```
3. 设置环境以及依赖:
   ```
   cp .env.example .env
   python -m venv venv 
   source ./venv/bin/activate  # Windows 使用 .\venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. 启动项目:
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8099
   ```
5. 访问应用：
    - API文档：http://localhost:8099/api/v1/docs

## 项目结构

```
FastAPIX
├── main.py                 # 应用入口文件
├── core                    # 核心配置
│   ├── __init__.py
│   ├── conf.py             # 项目配置
│   ├── path_conf.py        # 路径配置
│   ├── router.py           # 主路由注册
│   ├── registrar.py        # 应用注册与初始化
│   └── security.py         # 安全配置
├── engines                 # 数据库连接
│   ├── __init__.py
│   ├── mysql.py            # MySQL管理器
│   └── redis.py            # Redis连接
├── middleware              # 中间件组件
│   ├── __init__.py
│   ├── auth_middleware.py  # 认证中间件
│   ├── access_middleware.py# 访问日志中间件
│   ├── cors_middleware.py  # CORS跨域中间件
│   └── rate_limit_middleware.py  # 请求速率限制中间件
├── utils                   # 工具类
│   ├── __init__.py
│   ├── helpers.py          # 通用辅助函数
│   ├── log.py              # 日志配置
│   ├── response.py         # API响应格式化
│   ├── exception.py        # 全局异常处理
│   ├── serializers.py      # 序列化工具
│   ├── token_manager.py    # 令牌管理（支持Redis或内存存储）
│   └── security.py         # 安全相关工具(加密、token等)
├── apps                    # 业务模块目录
│   ├── __init__.py
│   ├── users               # 用户模块
│   │   ├── __init__.py
│   │   ├── models.py       # 用户数据库模型（供auth模块共享使用）
│   │   ├── repository.py   # 数据访问层
│   │   ├── schemas.py      # 数据验证和响应模型
│   │   ├── service.py      # 业务逻辑
│   │   ├── dependencies.py # 模块依赖注入
│   │   ├── handlers.py     # 请求处理层
│   │   └── router.py       # API路由
│   └── auth                # 认证模块
│       ├── __init__.py
│       ├── repository.py   # 数据访问层（使用users模块的User模型）
│       ├── schemas.py      # 数据验证和响应模型
│       ├── service.py      # 业务逻辑
│       ├── dependencies.py # 模块依赖注入
│       ├── handlers.py     # 请求处理层
│       └── router.py       # API路由
├── deploy                  # 部署相关
│   ├── docker_env          # Docker环境配置
│   │   ├── mysql           # MySQL Docker配置
│   │   │   ├── config      # MySQL配置
│   │   │   ├── data        # MySQL数据目录
│   │   │   └── log         # MySQL日志目录
│   │   └── redis           # Redis Docker配置
│   │       ├── data        # Redis数据目录
│   │       └── redis.conf  # Redis配置文件
│   └── gunicorn            # Gunicorn部署
│       ├── gunicorn_conf.py # Gunicorn配置
│       └── start.sh        # 启动脚本
├── sql                     # SQL脚本目录
│   └── schema.sql          # 数据库初始化和表结构定义（合并了init.sql）
├── requirements.txt        # 项目依赖
├── .env                    # 环境变量
├── .env.example            # 环境变量示例
├── docker-compose.yml      # Docker组合配置
├── .gitignore              # Git忽略文件
└── README.md               # 项目文档
```

### 目录结构设计优势

* **清晰的分层架构**：遵循「表现层-业务层-数据访问层」的三层架构
* **关注点分离**：配置、数据库连接、业务逻辑各自独立，职责明确
* **扁平化结构**：顶层目录清晰展示项目的主要组件，避免过深的嵌套
* **模块化设计**：apps 目录下按功能领域组织代码，便于扩展
* **依赖注入友好**：分离的 repository、service 和 handlers 层便于依赖注入和测试
* **符合 SOLID 原则**：单一职责、开放封闭、接口隔离

### 模块层次结构

* **Router 层**: 负责路由注册和配置，使用add_api_route方法注册路由
* **Handler 层**: 处理HTTP请求和响应，调用业务服务
* **Service 层**: 实现所有业务逻辑，协调多个资源
* **Repository 层**: 处理所有数据访问，与数据库交互
* **Model 层**: 定义数据库模型和关系
* **Schema 层**: 处理请求验证和响应序列化

## 开发指南

### 添加新功能

1. 在 `sql/schema.sql` 中定义新功能所需的表结构
2. 使用推荐的工具从数据库生成 SQLAlchemy 模型代码
3. 在 `apps` 目录下创建新的模块目录
4. 实现 models.py, repository.py, schemas.py, service.py 和 router.py
5. 在 `core/router.py` 中注册新的路由
6. 添加相应的单元测试

### 中间件系统

FastAPIX 利用中间件处理请求/响应生命周期中的横切关注点：

* **认证中间件 (AuthMiddleware)**：处理API认证，支持基于JWT的令牌验证和权限检查
* **访问日志中间件 (AccessMiddleware)**：记录所有API请求的访问日志，包括IP、方法、状态码和响应时间
* **CORS中间件**：处理跨域资源共享，允许从不同源访问API
* **速率限制中间件 (RateLimitMiddleware)**：限制API请求频率，防止API滥用，支持基于Redis的分布式限流

添加自定义中间件的步骤：

1. 在 `middleware` 目录中创建新的中间件文件
2. 实现中间件类或函数
3. 在 `middleware/__init__.py` 中导出中间件
4. 在应用启动时注册中间件

### 依赖注入系统

FastAPIX 充分利用 FastAPI 的依赖注入系统，帮助你：

* 模块化业务逻辑
* 隔离接口职责
* 显著提升可测试性
* 构建高可维护的大型应用

无论是构建微服务、后台管理系统，还是机器学习接口服务，推荐都采用 DI + 类型注解的方式构建接口和服务逻辑。

### 代码风格

- 遵循 PEP 8 编码规范
- 使用 Black 进行代码格式化
- 使用 isort 对导入进行排序
- 使用类型注解提高代码可读性和IDE支持

## 部署

1. 确保已正确设置所有环境变量。
2. 使用 `gunicorn` 和 `deploy/gunicorn.conf.py` 配置文件启动应用，执行如下命令启动：

```
cd deploy/gunicorn
chmod +x start.sh
./start.sh
```

3. 最后使用 Nginx 作为反向代理并配置域名。

### Docker 部署（可选）

项目提供了 Docker 支持，可以使用以下命令构建和运行容器：

```bash
# 构建镜像
docker build -t fastapiX:latest .

# 运行容器
docker run -d -p 8099:8099 --name fastapiX-app fastapiX:latest
```

## 版本控制

我们使用 [SemVer](http://semver.org/) 进行版本控制。查看 [tags on this repository](https://github.com/tao-xiaoxin/PicFast/-/tags) 以获取所有可用版本。

## 贡献指南

1. Fork 项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 致谢

* 感谢所有为这个项目做出贡献的团队成员。
* 特别感谢 [FastAPI](https://fastapi.tiangolo.com/) 框架提供的支持。