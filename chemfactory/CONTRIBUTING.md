# Contributing to ChemFactory MES/ERP

Thank you for your interest in contributing to ChemFactory MES/ERP! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- PostgreSQL (optional, SQLite for development)

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/chemfactory.git`
3. Run the development setup: `./run_dev.sh`
4. Access the application at `http://localhost:3000`

## 📋 Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript/JavaScript**: Use Prettier and ESLint
- **Commits**: Use conventional commit messages

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Pull Request Process
1. Create a feature branch from `main`
2. Make your changes
3. Add tests if applicable
4. Update documentation
5. Submit a pull request

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Run the full test suite
./run_dev.sh --test
```

## 📝 Documentation

### Code Documentation
- Use docstrings for Python functions
- Add JSDoc comments for TypeScript functions
- Include type hints and return types

### API Documentation
- Update OpenAPI schemas when adding new endpoints
- Include example requests and responses
- Document authentication requirements

### README Updates
- Update setup instructions if dependencies change
- Add new features to the features list
- Update demo data information

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/
│   ├── core/           # Settings, security, dependencies
│   ├── db/             # Models, schemas, database
│   ├── api/            # API routers
│   ├── services/       # Business logic
│   ├── repositories/   # Data access layer
│   └── utils/          # Utilities
```

### Frontend Structure
```
frontend/
├── app/
│   ├── [locale]/       # Internationalized routes
│   ├── _components/    # Reusable components
│   ├── _hooks/         # Custom React hooks
│   └── _lib/           # Utility functions
├── messages/           # Translation files
```

## 🌐 Internationalization

### Adding New Languages
1. Add language code to `frontend/i18n.ts`
2. Create translation file in `frontend/messages/[language].json`
3. Update locale validation in layout files
4. Test RTL support if applicable

### Translation Guidelines
- Use clear, concise language
- Maintain consistency across translations
- Consider cultural context
- Test with native speakers when possible

## 🔒 Security

### Security Guidelines
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security guidelines
- Report security issues privately

### Authentication
- Use JWT tokens for authentication
- Implement proper role-based access control
- Hash passwords with bcrypt
- Use HTTPS in production

## 🐛 Bug Reports

### Reporting Bugs
1. Check existing issues
2. Use the bug report template
3. Include steps to reproduce
4. Provide environment details
5. Add screenshots if applicable

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows, macOS, Linux]
- Browser: [e.g., Chrome, Firefox, Safari]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Suggesting Features
1. Check existing feature requests
2. Use the feature request template
3. Explain the use case
4. Consider implementation complexity
5. Discuss with maintainers

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context about the feature.
```

## 📊 Performance

### Performance Guidelines
- Optimize database queries
- Use appropriate caching strategies
- Minimize bundle size
- Implement lazy loading
- Monitor performance metrics

### Database Optimization
- Use proper indexing
- Avoid N+1 queries
- Use database connection pooling
- Monitor query performance

## 🚀 Deployment

### Deployment Guidelines
- Test in staging environment
- Use environment-specific configurations
- Monitor application health
- Implement proper logging
- Use CI/CD pipelines

### Environment Variables
- Document all required environment variables
- Use secure defaults
- Validate configuration on startup
- Never commit sensitive data

## 📞 Support

### Getting Help
- Check the documentation
- Search existing issues
- Join our community discussions
- Contact maintainers

### Community Guidelines
- Be respectful and inclusive
- Help others when possible
- Follow the code of conduct
- Report inappropriate behavior

## 📄 License

By contributing to ChemFactory MES/ERP, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to ChemFactory MES/ERP! 🎉
