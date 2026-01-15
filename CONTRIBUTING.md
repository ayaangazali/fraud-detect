# Contributing to Kamco Fraud Detection System

Thank you for considering contributing to the Kamco Fraud Detection System! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Harassment, trolling, or derogatory comments
- Public or private harassment
- Publishing others' private information
- Other unethical or unprofessional conduct

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.13+** installed
- **Node.js 20+** installed
- **Git** configured
- Code editor (VS Code recommended)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fraud-detect.git
   cd fraud-detect
   ```
3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ayaangazali/fraud-detect.git
   ```

### Setup Development Environment

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Seed database
python3 seed_database.py

# Run backend
python -m uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

## 🔄 Development Workflow

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions/updates
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

### Making Changes

1. **Write clear, concise code**
2. **Add tests** for new features
3. **Update documentation** as needed
4. **Test your changes** thoroughly

### Running Tests

#### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=routes --cov=utils --cov-report=html
```

#### Frontend Tests (when available)

```bash
cd frontend
npm run test
```

### Code Quality Checks

#### Python (Backend)

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

#### TypeScript (Frontend)

```bash
# Lint code
npm run lint

# Type checking
npm run type-check
```

## 📝 Coding Standards

### Python (Backend)

**Follow PEP 8 Style Guide:**

```python
# ✅ GOOD
def calculate_match_score(
    entity_name: str,
    blacklist_name: str,
    threshold: float = 0.85
) -> float:
    """
    Calculate similarity score between two names.
    
    Args:
        entity_name: Name from Kamco database
        blacklist_name: Name from blacklist
        threshold: Minimum similarity threshold
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    score = fuzz.token_sort_ratio(entity_name, blacklist_name) / 100.0
    return score if score >= threshold else 0.0


# ❌ BAD
def calc(n1,n2,t=0.85):
    s=fuzz.token_sort_ratio(n1,n2)/100.0
    return s if s>=t else 0.0
```

**Key Principles:**
- Use type hints for function parameters and return values
- Write docstrings for all public functions
- Keep functions under 50 lines
- Use meaningful variable names
- Prefer explicit over implicit

### TypeScript (Frontend)

**Follow React Best Practices:**

```typescript
// ✅ GOOD
interface ScreeningMatch {
  id: number;
  kamcoName: string;
  blacklistName: string;
  matchScore: number;
  riskLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

const ScreeningQueuePage: React.FC = () => {
  const [matches, setMatches] = useState<ScreeningMatch[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchMatches();
  }, []);
  
  const fetchMatches = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/screening/v2/pending-matches');
      setMatches(response.data.matches);
    } catch (error) {
      console.error('Failed to fetch matches:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="p-6">
      {/* Component JSX */}
    </div>
  );
};


// ❌ BAD
const Page = () => {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    apiClient.get('/api').then(r => setData(r.data.matches));
  }, []);
  
  return <div>{/* JSX */}</div>;
};
```

**Key Principles:**
- Use TypeScript for type safety
- Use functional components with hooks
- Keep components under 200 lines
- Extract reusable logic into custom hooks
- Use meaningful prop names

## 🧪 Testing Guidelines

### Writing Tests

#### Backend Test Example

```python
# tests/test_screening.py

def test_upload_blacklist_success(client, authenticated_screener):
    """Test successful blacklist upload"""
    # Arrange
    csv_data = "name_english,civil_id\nJohn Doe,123456789"
    files = {"file": ("blacklist.csv", csv_data, "text/csv")}
    
    # Act
    response = client.post(
        "/api/screening/v2/upload-blacklist",
        files=files,
        headers={"Authorization": f"Bearer {authenticated_screener}"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "matches_found" in data
```

#### Frontend Test Example

```typescript
// __tests__/ScreeningQueue.test.tsx

describe('ScreeningQueuePage', () => {
  it('should display matches when loaded', async () => {
    // Arrange
    const mockMatches = [
      { id: 1, kamcoName: 'John Doe', matchScore: 0.95 }
    ];
    jest.spyOn(apiClient, 'get').mockResolvedValue({
      data: { matches: mockMatches }
    });
    
    // Act
    render(<ScreeningQueuePage />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });
});
```

### Test Coverage Requirements

- **Minimum coverage:** 80%
- **New features:** Must include tests
- **Bug fixes:** Must include regression tests

## 💬 Commit Message Convention

We follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(screening): Add individual person screening endpoint"

# Bug fix
git commit -m "fix(auth): Resolve token refresh infinite loop"

# Documentation
git commit -m "docs(readme): Update installation instructions"

# Refactoring
git commit -m "refactor(matching): Extract fuzzy matching into separate utility"

# Multiple lines
git commit -m "feat(dashboard): Add real-time statistics

- Add KPI cards for total screenings, flagged items
- Implement risk distribution chart
- Add recent activity feed

Closes #42"
```

### Commit Message Rules

- ✅ Use imperative mood ("Add feature" not "Added feature")
- ✅ First line under 72 characters
- ✅ Capitalize first letter
- ✅ No period at the end of subject line
- ✅ Separate subject from body with blank line
- ✅ Reference issues in footer

## 🔀 Pull Request Process

### Before Submitting

1. **Update your branch:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Run tests:**
   ```bash
   # Backend
   cd backend
   pytest tests/ -v
   
   # Frontend
   cd frontend
   npm run test
   ```

3. **Check code quality:**
   ```bash
   # Python
   black backend/
   flake8 backend/
   
   # TypeScript
   npm run lint
   ```

### Creating Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature
   ```

2. **Open PR on GitHub:**
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill out the PR template

3. **PR Title Format:**
   ```
   feat(scope): Brief description
   ```

4. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] All tests pass
   - [ ] New tests added
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   
   ## Screenshots (if applicable)
   
   ## Related Issues
   Closes #issue_number
   ```

### Review Process

1. **Automated checks** will run (tests, linting)
2. **Code review** by maintainers
3. **Address feedback** by pushing new commits
4. **Approval** and merge by maintainers

### After Merge

1. **Delete your branch:**
   ```bash
   git checkout main
   git pull upstream main
   git branch -d feature/your-feature
   git push origin --delete feature/your-feature
   ```

2. **Update your fork:**
   ```bash
   git push origin main
   ```

## 🏗️ Project Structure

Understanding the project structure:

```
fraud-detect/
├── backend/              # FastAPI backend
│   ├── routes/           # API endpoints
│   ├── models/           # Database models
│   ├── utils/            # Helper functions
│   ├── middleware/       # Auth & audit middleware
│   └── tests/            # Test suite
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Route pages
│   │   └── services/     # API services
│   └── tests/            # Frontend tests
│
└── docs/                 # Documentation
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Python PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 💡 Need Help?

- 📧 **Email**: support@kamco.com
- 💬 **GitHub Issues**: [Create an issue](https://github.com/ayaangazali/fraud-detect/issues)
- 📚 **Documentation**: [Read the docs](https://github.com/ayaangazali/fraud-detect/wiki)

## 🙏 Recognition

Contributors will be recognized in the project README. Thank you for making this project better!

---

**Happy Contributing! 🎉**
