# 🎨 Frontend Development Guide
## Medical Text Classification React App

Comprehensive guide for developing, customizing, and maintaining the React-based frontend application.

## 🏗️ Architecture Overview

### Technology Stack
- **React 18** with TypeScript
- **Material-UI (MUI)** for component library
- **Axios** for API communication
- **React Router** for navigation
- **React Hook Form** for form management
- **React Query** for data fetching and caching

### Project Structure
```
frontend/
├── public/
│   ├── index.html              # HTML template
│   ├── manifest.json           # PWA manifest
│   └── favicon.ico             # App icon
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── ClassificationForm.tsx
│   │   ├── ResultDisplay.tsx
│   │   ├── HealthStatus.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── Layout/
│   ├── pages/                  # Page components
│   │   ├── Home.tsx
│   │   ├── About.tsx
│   │   └── NotFound.tsx
│   ├── services/               # API and external services
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── config.ts
│   ├── hooks/                  # Custom React hooks
│   │   ├── useClassification.ts
│   │   ├── useHealth.ts
│   │   └── useApi.ts
│   ├── utils/                  # Utility functions
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── constants.ts
│   ├── styles/                 # Global styles and themes
│   │   ├── theme.ts
│   │   ├── globals.css
│   │   └── components.css
│   ├── App.tsx                 # Main app component
│   ├── index.tsx               # App entry point
│   └── setupTests.ts           # Test configuration
├── package.json                # Dependencies and scripts
├── tsconfig.json              # TypeScript configuration
└── .env                       # Environment variables
```

## 🔧 Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- TypeScript knowledge

### Installation
```bash
cd frontend
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint
```

### Environment Configuration
Create `.env` file in the frontend directory:
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG=true

# UI Configuration
REACT_APP_THEME=light
REACT_APP_BRAND_NAME=Medical Text Classifier
```

## 🎯 Core Components

### 1. ClassificationForm Component

**Purpose**: Main form for text input and classification requests.

<augment_code_snippet path="frontend/src/components/ClassificationForm.tsx" mode="EXCERPT">
````typescript
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { useClassification } from '../hooks/useClassification';

interface ClassificationFormProps {
  onResult: (result: ClassificationResult) => void;
}

export const ClassificationForm: React.FC<ClassificationFormProps> = ({
  onResult
}) => {
  const [text, setText] = useState('');
  const { classify, loading, error } = useClassification();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      const result = await classify(text);
      if (result) {
        onResult(result);
      }
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Enter Medical Text for Classification
      </Typography>
      
      <TextField
        fullWidth
        multiline
        rows={4}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter your medical question or text here..."
        variant="outlined"
        sx={{ mb: 2 }}
        inputProps={{
          maxLength: 5000
        }}
      />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {text.length}/5000 characters
        </Typography>
        
        <Button
          type="submit"
          variant="contained"
          disabled={loading || !text.trim()}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? 'Classifying...' : 'Classify Text'}
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};
````
</augment_code_snippet>

### 2. ResultDisplay Component

**Purpose**: Display classification results with confidence scores and visualizations.

<augment_code_snippet path="frontend/src/components/ResultDisplay.tsx" mode="EXCERPT">
````typescript
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Grid
} from '@mui/material';
import { ClassificationResult } from '../services/types';

interface ResultDisplayProps {
  result: ClassificationResult;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  const focusGroups = [
    'Neurological & Cognitive Disorders',
    'Cancers',
    'Cardiovascular Diseases',
    'Metabolic & Endocrine Disorders',
    'Other Age-Related & Immune Disorders'
  ];

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Classification Result
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" color="primary" gutterBottom>
            {result.focus_group}
          </Typography>
          <Chip
            label={`${(result.confidence * 100).toFixed(1)}% Confidence`}
            color="success"
            variant="outlined"
          />
        </Box>
        
        <Typography variant="subtitle1" gutterBottom>
          Probability Distribution
        </Typography>
        
        <Grid container spacing={2}>
          {result.probabilities.map((prob, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" gutterBottom>
                  {focusGroups[index]}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={prob * 100}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {(prob * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
        
        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Processing time: {result.processing_time_ms}ms | 
            Model: {result.model_version}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
````
</augment_code_snippet>

### 3. HealthStatus Component

**Purpose**: Display system health and status information.

<augment_code_snippet path="frontend/src/components/HealthStatus.tsx" mode="EXCERPT">
````typescript
import React from 'react';
import {
  Box,
  Chip,
  Typography,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import { CheckCircle, Error, Warning } from '@mui/icons-material';
import { useHealth } from '../hooks/useHealth';

export const HealthStatus: React.FC = () => {
  const { health, loading, error } = useHealth();

  if (loading) return <Typography>Checking system health...</Typography>;
  if (error) return <Typography color="error">Health check failed</Typography>;
  if (!health) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'degraded':
        return <Warning color="warning" />;
      case 'unhealthy':
        return <Error color="error" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {getStatusIcon(health.status)}
          <Typography variant="h6" sx={{ ml: 1 }}>
            System Status
          </Typography>
          <Chip
            label={health.status.toUpperCase()}
            color={getStatusColor(health.status) as any}
            size="small"
            sx={{ ml: 'auto' }}
          />
        </Box>
        
        <Grid container spacing={2}>
          {Object.entries(health.components).map(([component, details]) => (
            <Grid item xs={12} sm={6} md={4} key={component}>
              <Box sx={{ p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  {component.charAt(0).toUpperCase() + component.slice(1)}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {getStatusIcon(details.status)}
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    {details.status}
                  </Typography>
                </Box>
                {details.response_time_ms && (
                  <Typography variant="caption" color="text.secondary">
                    {details.response_time_ms}ms
                  </Typography>
                )}
              </Box>
            </Grid>
          ))}
        </Grid>
        
        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Uptime: {Math.floor(health.uptime_seconds / 3600)}h | 
            Requests: {health.request_count} | 
            Error Rate: {(health.error_rate * 100).toFixed(2)}%
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
````
</augment_code_snippet>

## 🎣 Custom Hooks

### 1. useClassification Hook

**Purpose**: Handle text classification logic and state management.

<augment_code_snippet path="frontend/src/hooks/useClassification.ts" mode="EXCERPT">
````typescript
import { useState, useCallback } from 'react';
import { classifyText } from '../services/api';
import { ClassificationResult } from '../services/types';

export const useClassification = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClassificationResult | null>(null);

  const classify = useCallback(async (text: string): Promise<ClassificationResult | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await classifyText(text);
      setResult(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Classification failed';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    classify,
    reset,
    loading,
    error,
    result
  };
};
````
</augment_code_snippet>

### 2. useHealth Hook

**Purpose**: Monitor system health status.

<augment_code_snippet path="frontend/src/hooks/useHealth.ts" mode="EXCERPT">
````typescript
import { useState, useEffect } from 'react';
import { getHealth } from '../services/api';
import { HealthResponse } from '../services/types';

export const useHealth = (interval: number = 30000) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const healthData = await getHealth();
        setHealth(healthData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Health check failed');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchHealth();

    // Set up interval for periodic health checks
    const intervalId = setInterval(fetchHealth, interval);

    return () => clearInterval(intervalId);
  }, [interval]);

  return { health, loading, error };
};
````
</augment_code_snippet>

## 🎨 Theming and Styling

### Material-UI Theme Configuration

<augment_code_snippet path="frontend/src/styles/theme.ts" mode="EXCERPT">
````typescript
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#ed6c02',
    },
    error: {
      main: '#d32f2f',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});
````
</augment_code_snippet>

## 🔌 API Integration

### API Service Configuration

<augment_code_snippet path="frontend/src/services/api.ts" mode="EXCERPT">
````typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ClassificationRequest, ClassificationResult, HealthResponse } from './types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add API key if available
    const apiKey = process.env.REACT_APP_API_KEY;
    if (apiKey) {
      this.client.defaults.headers.common['X-API-Key'] = apiKey;
    }

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  async classifyText(text: string): Promise<ClassificationResult> {
    const response = await this.client.post<ClassificationResult>('/predict', { text });
    return response.data;
  }

  async getHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export const classifyText = (text: string) => apiService.classifyText(text);
export const getHealth = () => apiService.getHealth();
````
</augment_code_snippet>

## 🧪 Testing

### Component Testing with React Testing Library

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ClassificationForm } from '../components/ClassificationForm';
import { apiService } from '../services/api';

// Mock API service
jest.mock('../services/api');
const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('ClassificationForm', () => {
  const mockOnResult = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form elements correctly', () => {
    render(<ClassificationForm onResult={mockOnResult} />);
    
    expect(screen.getByText('Enter Medical Text for Classification')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your medical question/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Classify Text/ })).toBeInTheDocument();
  });

  test('submits form with valid text', async () => {
    const mockResult = {
      predicted_class: 3,
      confidence: 0.95,
      focus_group: 'Metabolic & Endocrine Disorders',
      probabilities: [0.01, 0.02, 0.01, 0.95, 0.01],
      processing_time_ms: 87.3,
      model_version: 'biomedbert-v1.0',
      timestamp: '2024-01-15T10:30:00Z'
    };

    mockApiService.classifyText.mockResolvedValue(mockResult);

    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });

    fireEvent.change(textInput, { target: { value: 'What are the symptoms of diabetes?' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiService.classifyText).toHaveBeenCalledWith('What are the symptoms of diabetes?');
      expect(mockOnResult).toHaveBeenCalledWith(mockResult);
    });
  });

  test('displays error message on API failure', async () => {
    mockApiService.classifyText.mockRejectedValue(new Error('API Error'));

    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });

    fireEvent.change(textInput, { target: { value: 'Test text' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });
});
```

## 🚀 Build and Deployment

### Development Build
```bash
npm start
# Starts development server on http://localhost:3000
# Hot reloading enabled
# Source maps included
```

### Production Build
```bash
npm run build
# Creates optimized production build in build/ directory
# Minified and compressed assets
# Source maps excluded
```

### Build Optimization
- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Remove unused code
- **Asset Optimization**: Image compression and optimization
- **Bundle Analysis**: Use `npm run analyze` to analyze bundle size

### Environment Variables
```bash
# Production environment
REACT_APP_API_URL=https://medtext-api.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DEBUG=false
```

## 📱 Progressive Web App (PWA)

The frontend is configured as a PWA with:
- **Service Worker**: Offline caching and background sync
- **Web App Manifest**: Install prompts and app-like experience
- **Responsive Design**: Mobile-first responsive layout
- **Offline Support**: Basic offline functionality

### PWA Configuration
```json
{
  "name": "Medical Text Classification",
  "short_name": "MedText",
  "description": "AI-powered medical text classification",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#1976d2",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

## 🔧 Customization Guide

### Adding New Components
1. Create component in `src/components/`
2. Export from `src/components/index.ts`
3. Add TypeScript interfaces in `src/services/types.ts`
4. Write tests in `src/components/__tests__/`

### Modifying Themes
1. Update `src/styles/theme.ts`
2. Add custom CSS in `src/styles/components.css`
3. Use Material-UI's `sx` prop for component-specific styles

### Adding New API Endpoints
1. Add types to `src/services/types.ts`
2. Add methods to `src/services/api.ts`
3. Create custom hooks in `src/hooks/`
4. Update components to use new hooks

---

## 🎯 Best Practices

### 1. **Component Design**
- Keep components small and focused
- Use TypeScript for type safety
- Implement proper error boundaries
- Follow Material-UI design patterns

### 2. **State Management**
- Use React hooks for local state
- Implement custom hooks for business logic
- Consider React Query for server state
- Avoid prop drilling with context

### 3. **Performance**
- Implement React.memo for expensive components
- Use useCallback and useMemo appropriately
- Lazy load routes and components
- Optimize bundle size with code splitting

### 4. **Accessibility**
- Use semantic HTML elements
- Implement proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers

### 5. **Testing**
- Write unit tests for components
- Test user interactions
- Mock external dependencies
- Maintain high test coverage

This frontend provides a solid foundation for the medical text classification application with modern React patterns, comprehensive testing, and production-ready optimizations.
