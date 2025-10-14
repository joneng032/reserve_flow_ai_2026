# Frontend - Authentication API

Frontend application built with Vite + React + TypeScript that consumes the authentication API.

## 🚀 Features

- **Vite** - Fast build tool with hot reload
- **React 18** - UI Framework
- **TypeScript** - Static typing
- **Tailwind CSS** - Styling framework
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **Yup** - Schema validation

## 📦 Installation

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:3000/api
```

### Backend API

Make sure the backend is running on `http://localhost:3000`

## 🎯 Features

### Authentication

- Login form with validation
- JWT token storage in localStorage
- Automatic redirect to dashboard
- Error handling

### Dashboard

- Authenticated user information
- System user list
- User status (active/inactive)
- Logout

### UI/UX

- Responsive design with Tailwind CSS
- Loading states
- Error handling
- Smooth animations

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   │   ├── LoginForm.tsx
│   │   └── Dashboard.tsx
│   ├── services/       # API services
│   │   └── api.ts
│   ├── types/          # TypeScript types
│   │   └── api.ts
│   ├── App.tsx         # Main component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # Main HTML
├── package.json        # Node.js dependencies
├── tailwind.config.js  # Tailwind configuration
├── postcss.config.js   # PostCSS configuration
├── tsconfig.json       # TypeScript configuration
└── vite.config.ts      # Vite configuration
```

## 🔌 Consumed Endpoints

- `POST /api/login` - Authentication
- `GET /api/protected` - User information
- `GET /api/users` - User list

## 🎨 Used Technologies

- **Vite** - Build tool and dev server
- **React** - UI Framework
- **TypeScript** - Static typing
- **Tailwind CSS** - Styling framework
- **React Hook Form** - Form handling
- **Yup** - Schema validation
- **Axios** - HTTP client

## 🚀 Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev
```

The application will be available at `http://localhost:5173`

## 🔧 Available Scripts

- `npm run dev` - Development server
- `npm run build` - Build for production
- `npm run preview` - Preview build
- `npm run lint` - ESLint linting

## 📱 Responsive Design

The application is fully optimized for:

- 📱 Mobiles (320px+)
- 📱 Tablets (768px+)
- 💻 Desktop (1024px+)

## 🔒 Security

- JWT tokens stored in localStorage
- Axios interceptors for automatic token handling
- Automatic redirect on token expiration
- Frontend form validation

## 🎯 Next Steps

- [ ] Implement refresh tokens
- [ ] Add more pages (profile, settings)
- [ ] Implement toast notifications
- [ ] Add unit tests
- [ ] Implement PWA
