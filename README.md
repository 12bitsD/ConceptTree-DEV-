# ConceptTree

> AI驱动的概念依赖树可视化学习工具

## 快速开始

### 启动前端
```bash
cd frontend
npm run dev
```

### 启动后端
```bash
cd backend
python -m app.main
```

## 技术栈

- **前端:** React 19 + Vite + ReactFlow
- **后端:** FastAPI + Python
- **设计:** CodeMonkey Design System

## 项目结构

```
ConceptTree-New/
├── frontend/           # React前端
├── backend/            # FastAPI后端
└── docs/               # 开发文档
```

## 文档

- [开发指引](docs/DEVELOPMENT.md) - API文档、前后端对接、联调步骤
- [脚手架说明](docs/SCAFFOLD_README.md) - 项目状态和核心任务
- [设计系统](docs/CodeMonkey-design-system.md) - UI设计规范

## TODO

- [ ] 实现AI服务 (`backend/app/services/ai_service.py`)
- [ ] 配置MiniMax API
- [ ] 前后端联调测试

## License

MIT
