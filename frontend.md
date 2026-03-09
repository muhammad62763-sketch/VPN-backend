# VPN Mobile Application - Frontend Documentation

**Version:** 1.0.0  
**Last Updated:** 2026-03-08  
**Platform:** React Native (iOS & Android)  
**Backend API:** FastAPI VPN Backend v2.0

---

## 1. Frontend Overview

### Purpose
The VPN mobile application provides users with a secure, intuitive interface to manage their VPN connections, select servers from 40+ countries, monitor bandwidth usage, and manage their account settings. The app communicates with the FastAPI backend through RESTful APIs with JWT authentication.

### Main Goals
- **Performance:** Fast app startup (<2s), smooth animations (60fps), efficient memory usage
- **Usability:** Intuitive navigation, one-tap VPN connection, clear server selection
- **Scalability:** Modular architecture supporting future features (premium tiers, referrals, 2FA)
- **Maintainability:** Clean code structure, TypeScript for type safety, comprehensive documentation
- **Security:** Secure token storage, encrypted API communication, input validation

### Key Features
- One-tap VPN connection/disconnection
- Server selection with country flags and load indicators
- Real-time bandwidth monitoring
- Connection history and analytics
- Account management (profile, settings, 2FA)
- Premium features (premium servers, unlimited bandwidth)
- Referral system
- Push notifications
- Dark/Light theme support

---

## 2. Recommended Technology Stack (2025+ Standard)

### Core Framework
```json
{
  "react-native": "0.73.x",
  "expo": "~50.0.0",
  "typescript": "^5.3.0"
}
```

**Why Expo?**
- Faster development with managed workflow
- Built-in OTA updates
- Easy build and deployment
- Excellent developer experience
- Native module support with custom dev clients

### Navigation
```json
{
  "@react-navigation/native": "^6.1.9",
  "@react-navigation/stack": "^6.3.20",
  "@react-navigation/bottom-tabs": "^6.5.11",
  "@react-navigation/drawer": "^6.6.6"
}
```

### State Management
```json
{
  "zustand": "^4.4.7"
}
```

**Why Zustand?**
- Lightweight (1KB)
- Simple API
- No boilerplate
- TypeScript-first
- Perfect for VPN connection state

### API Communication
```json
{
  "axios": "^1.6.2",
  "react-query": "^3.39.3"
}
```

**Why React Query?**
- Automatic caching
- Background refetching
- Optimistic updates
- Perfect for server list and user data

### Form Management & Validation
```json
{
  "react-hook-form": "^7.49.2",
  "zod": "^3.22.4"
}
```

### UI Component Library
```json
{
  "react-native-paper": "^5.11.3",
  "@react-native-vector-icons": "^10.0.3",
  "react-native-svg": "^14.1.0"
}
```

### Animation & Gestures
```json
{
  "react-native-reanimated": "^3.6.1",
  "react-native-gesture-handler": "^2.14.1",
  "lottie-react-native": "^6.4.1"
}
```

### Security
```json
{
  "expo-secure-store": "~12.8.1",
  "react-native-keychain": "^8.1.2"
}
```

### Additional Tools
```json
{
  "date-fns": "^3.0.6",
  "react-native-country-picker-modal": "^2.0.0",
  "react-native-chart-kit": "^6.12.0",
  "react-native-toast-message": "^2.2.0"
}
```

---

## 3. Mobile App Folder Structure

```
vpn-mobile/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── vpn/
│   │   │   ├── ServerCard.tsx
│   │   │   ├── ConnectionButton.tsx
│   │   │   ├── BandwidthMeter.tsx
│   │   │   └── ServerList.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── BottomNav.tsx
│   │       └── ScreenContainer.tsx
│   │
│   ├── screens/              # App screens
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   ├── ForgotPasswordScreen.tsx
│   │   │   └── VerifyEmailScreen.tsx
│   │   ├── main/
│   │   │   ├── HomeScreen.tsx
│   │   │   ├── ServersScreen.tsx
│   │   │   ├── ProfileScreen.tsx
│   │   │   └── SettingsScreen.tsx
│   │   ├── vpn/
│   │   │   ├── ConnectionScreen.tsx
│   │   │   ├── ServerDetailsScreen.tsx
│   │   │   └── ConnectionHistoryScreen.tsx
│   │   └── premium/
│   │       ├── PremiumScreen.tsx
│   │       └── ReferralScreen.tsx
│   │
│   ├── navigation/           # Navigation configuration
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   ├── MainNavigator.tsx
│   │   └── types.ts
│   │
│   ├── services/             # API services
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── vpn.ts
│   │   │   ├── user.ts
│   │   │   └── admin.ts
│   │   ├── vpn/
│   │   │   ├── connection.ts
│   │   │   └── wireguard.ts
│   │   └── storage/
│   │       ├── secureStorage.ts
│   │       └── asyncStorage.ts
│   │
│   ├── store/                # State management
│   │   ├── authStore.ts
│   │   ├── vpnStore.ts
│   │   ├── userStore.ts
│   │   └── settingsStore.ts
│   │
│   ├── hooks/                # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useVPN.ts
│   │   ├── useServers.ts
│   │   ├── useBandwidth.ts
│   │   └── useTheme.ts
│   │
│   ├── utils/                # Utility functions
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   │
│   ├── types/                # TypeScript types
│   │   ├── api.ts
│   │   ├── vpn.ts
│   │   ├── user.ts
│   │   └── navigation.ts
│   │
│   ├── theme/                # Theme configuration
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   ├── spacing.ts
│   │   └── theme.ts
│   │
│   └── assets/               # Static assets
│       ├── images/
│       ├── icons/
│       ├── fonts/
│       └── animations/
│
├── App.tsx                   # Root component
├── app.json                  # Expo configuration
├── package.json
├── tsconfig.json
└── babel.config.js
```

---

## 4. Core Screens to Implement

### Authentication Screens

#### 4.1 Login Screen
**Route:** `/auth/login`

**Features:**
- Email/password input fields
- "Remember me" toggle
- "Forgot password?" link
- Social login buttons (optional)
- Password visibility toggle
- Form validation with error messages
- Loading state during authentication

**API Endpoint:** `POST /api/v1/auth/login`

**Required Fields:**
```typescript
{
  email: string;
  password: string;
  device_id: string;
}
```

**Success Response:**
```typescript
{
  access_token: string;
  refresh_token: string;
  expires_in: number;
}
```

#### 4.2 Register Screen
**Route:** `/auth/register`

**Features:**
- Email input with validation
- Password input with strength indicator
- Confirm password field
- Terms & conditions checkbox
- Device ID auto-generation
- Real-time validation feedback

**API Endpoint:** `POST /api/v1/auth/register`

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

#### 4.3 Forgot Password Screen
**Route:** `/auth/forgot-password`

**Features:**
- Email input
- Send reset link button
- Success confirmation message
- Resend timer (60 seconds)

**API Endpoints:**
- `POST /api/v1/email/request-password-reset`
- `POST /api/v1/email/reset-password`

#### 4.4 Email Verification Screen
**Route:** `/auth/verify-email`

**Features:**
- Verification code input (6 digits)
- Resend code button
- Auto-submit on complete
- Timer countdown

**API Endpoint:** `POST /api/v1/email/verify-email`

---

### Main Application Screens

#### 4.5 Home/Dashboard Screen
**Route:** `/main/home`

**Features:**
- Large connection button (Connect/Disconnect)
- Current connection status
- Connected server info (country, city, flag)
- Real-time bandwidth usage (upload/download)
- Connection timer
- Quick server switch
- Premium upgrade banner (for free users)

**Components:**
- ConnectionButton (large, animated)
- ServerInfo card
- BandwidthMeter (live chart)
- ConnectionTimer
- QuickActions (recent servers)

#### 4.6 Servers Screen
**Route:** `/main/servers`

**Features:**
- Searchable server list
- Filter by region/country
- Sort by load, distance, speed
- Server cards showing:
  - Country flag
  - Country name & city
  - Load percentage (color-coded)
  - Premium badge (if premium server)
  - Ping/latency
- Pull-to-refresh
- Favorite servers

**API Endpoint:** `GET /api/v1/vpn/servers`

**Server Card Design:**
```
┌─────────────────────────────────┐
│ 🇺🇸  United States              │
│     Virginia                    │
│                                 │
│ Load: ████░░░░░░ 45%           │
│ Ping: 23ms          [PREMIUM]  │
│                      [CONNECT] │
└─────────────────────────────────┘
```

#### 4.7 Connection History Screen
**Route:** `/vpn/history`

**Features:**
- List of past connections
- Connection details:
  - Server connected to
  - Duration
  - Data transferred
  - Timestamp
- Filter by date range
- Export history (CSV)

**API Endpoint:** `GET /api/v1/vpn/stats`

#### 4.8 Profile Screen
**Route:** `/main/profile`

**Features:**
- User avatar (editable)
- Email address
- Account type (Free/Premium)
- Premium expiry date
- Account statistics:
  - Total connections
  - Total data transferred
  - Active devices
- Manage devices
- 2FA settings
- Referral code section

**API Endpoints:**
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET /api/v1/2fa/status`

#### 4.9 Settings Screen
**Route:** `/main/settings`

**Features:**
- **General:**
  - Auto-connect on app start
  - Auto-reconnect on disconnect
  - Kill switch (block internet if VPN drops)
  - Protocol selection (WireGuard)
  
- **Appearance:**
  - Theme (Light/Dark/Auto)
  - Language selection
  
- **Notifications:**
  - Connection status notifications
  - Data usage alerts
  - Premium expiry reminders
  
- **Security:**
  - Enable 2FA
  - Change password
  - Manage API keys
  - Active sessions
  
- **About:**
  - App version
  - Privacy policy
  - Terms of service
  - Contact support
  - Logout

#### 4.10 Premium Screen
**Route:** `/premium`

**Features:**
- Premium benefits list:
  - Access to premium servers
  - Unlimited bandwidth
  - Priority support
  - No ads
- Pricing plans (if applicable)
- Current plan status
- Upgrade button
- Referral rewards info

#### 4.11 Referral Screen
**Route:** `/referral`

**Features:**
- User's referral code (large, copyable)
- Share button (native share sheet)
- Referral statistics:
  - Total referrals
  - Successful referrals
  - Rewards earned
- Referral history list
- Create new referral code

**API Endpoints:**
- `POST /api/v1/referrals/create`
- `GET /api/v1/referrals/my-codes`
- `GET /api/v1/referrals/stats`

#### 4.12 Notifications Screen
**Route:** `/notifications`

**Features:**
- List of notifications
- Mark as read/unread
- Delete notifications
- Filter by type
- Unread count badge

**API Endpoints:**
- `GET /api/v1/notifications/`
- `POST /api/v1/notifications/{id}/read`
- `DELETE /api/v1/notifications/{id}`

#### 4.13 Bandwidth Usage Screen
**Route:** `/bandwidth`

**Features:**
- Current period usage (chart)
- Daily/weekly/monthly views
- Upload vs download breakdown
- Usage alerts configuration
- Historical data

**API Endpoints:**
- `GET /api/v1/bandwidth/usage`
- `GET /api/v1/bandwidth/current-period`

---

## 5. Navigation Architecture

### Navigation Structure

```typescript
AppNavigator (Root)
├── AuthNavigator (Stack)
│   ├── Login
│   ├── Register
│   ├── ForgotPassword
│   └── VerifyEmail
│
└── MainNavigator (Drawer)
    ├── TabNavigator (Bottom Tabs)
    │   ├── Home
    │   ├── Servers
    │   ├── History
    │   └── Profile
    │
    ├── Settings (Stack)
    ├── Premium (Stack)
    ├── Referral (Stack)
    ├── Notifications (Stack)
    └── Bandwidth (Stack)
```

### Implementation Example

```typescript
// navigation/AppNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { useAuthStore } from '@/store/authStore';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';

export default function AppNavigator() {
  const { isAuthenticated } = useAuthStore();
  
  return (
    <NavigationContainer>
      {isAuthenticated ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
```

### Stack Navigation
Use for linear flows:
- Authentication flow
- Settings screens
- Server details
- Profile editing

### Bottom Tab Navigation
Use for main app sections:
- Home (VPN connection)
- Servers (server list)
- History (connection history)
- Profile (user profile)

### Drawer Navigation
Use for secondary features:
- Settings
- Premium
- Referrals
- Notifications
- Help & Support
- Logout

---

## 6. Recommended UI Component Libraries

### Primary: React Native Paper
**Why?**
- Material Design 3 components
- Excellent theming support
- Built-in dark mode
- TypeScript support
- Active maintenance

**Key Components:**
- Button, FAB, IconButton
- TextInput, Searchbar
- Card, Surface
- List, Divider
- Dialog, Portal, Modal
- Snackbar, Banner
- ProgressBar, ActivityIndicator
- Switch, Checkbox, RadioButton

### Icons: React Native Vector Icons
**Collections to use:**
- MaterialCommunityIcons (primary)
- Ionicons (iOS-style)
- FontAwesome5 (social icons)

### Charts: React Native Chart Kit
**For:**
- Bandwidth usage graphs
- Connection statistics
- Data usage over time

### Country Flags: react-native-country-picker-modal
**For:**
- Server selection
- Country flags display

---

## 7. Essential UI Components

### Layout Components

#### 7.1 Header Component
```typescript
interface HeaderProps {
  title: string;
  showBack?: boolean;
  rightAction?: React.ReactNode;
  onBackPress?: () => void;
}
```

**Features:**
- App logo/title
- Back button (conditional)
- Right action buttons (notifications, settings)
- Elevation/shadow
- Theme-aware colors

#### 7.2 Bottom Navigation
**Tabs:**
1. Home (shield icon)
2. Servers (globe icon)
3. History (clock icon)
4. Profile (user icon)

**Features:**
- Active tab indicator
- Badge for notifications
- Smooth transitions
- Haptic feedback

#### 7.3 Screen Container
```typescript
interface ScreenContainerProps {
  children: React.ReactNode;
  scrollable?: boolean;
  loading?: boolean;
  error?: string;
  onRefresh?: () => void;
}
```

**Features:**
- Safe area handling
- Pull-to-refresh
- Loading state
- Error state
- Keyboard avoiding view

### Input Components

#### 7.4 Text Input
```typescript
interface TextInputProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  secureTextEntry?: boolean;
  keyboardType?: KeyboardType;
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
}
```

**Features:**
- Floating label
- Error message display
- Character counter
- Clear button
- Password visibility toggle

#### 7.5 Password Field
**Special Features:**
- Show/hide password toggle
- Password strength indicator
- Real-time validation feedback
- Copy/paste prevention (optional)

#### 7.6 Dropdown Selector
```typescript
interface DropdownProps {
  label: string;
  value: string;
  options: Array<{ label: string; value: string }>;
  onSelect: (value: string) => void;
}
```

**Use Cases:**
- Country selection
- Protocol selection
- Language selection

#### 7.7 Toggle Switch
**Use Cases:**
- Auto-connect
- Kill switch
- Dark mode
- Notifications

### Display Components

#### 7.8 Server Card
```typescript
interface ServerCardProps {
  server: {
    id: string;
    country: string;
    countryCode: string;
    city: string;
    loadPercent: number;
    isPremium: boolean;
    ping?: number;
  };
  onConnect: () => void;
  isConnected?: boolean;
}
```

**Design:**
- Country flag (large)
- Country & city name
- Load bar (color-coded: green <50%, yellow 50-80%, red >80%)
- Premium badge
- Ping indicator
- Connect button

#### 7.9 Connection Button
```typescript
interface ConnectionButtonProps {
  isConnected: boolean;
  isConnecting: boolean;
  onPress: () => void;
}
```

**States:**
- Disconnected (gray, "Connect")
- Connecting (animated, "Connecting...")
- Connected (green, "Disconnect")

**Animation:**
- Pulse effect when connecting
- Ripple effect on press
- Color transition

#### 7.10 Bandwidth Meter
```typescript
interface BandwidthMeterProps {
  uploadSpeed: number; // bytes/sec
  downloadSpeed: number; // bytes/sec
  totalUploaded: number; // bytes
  totalDownloaded: number; // bytes
}
```

**Display:**
- Real-time upload/download speeds
- Animated arrows (up/down)
- Total data transferred
- Speed chart (optional)

#### 7.11 Connection Status Card
**Information:**
- Connection status (Connected/Disconnected)
- Connected server
- IP address (before/after)
- Connection duration
- Protocol used

#### 7.12 Statistics Card
**Metrics:**
- Total connections
- Total data transferred
- Average session duration
- Favorite server

### Feedback Components

#### 7.13 Toast Notifications
**Types:**
- Success (green)
- Error (red)
- Warning (yellow)
- Info (blue)

**Use Cases:**
- Connection success/failure
- Settings saved
- API errors
- Network issues

**Library:** `react-native-toast-message`

#### 7.14 Loading Spinner
**Types:**
- Full-screen overlay
- Inline spinner
- Button loading state
- Skeleton loaders

#### 7.15 Error State
```typescript
interface ErrorStateProps {
  title: string;
  message: string;
  onRetry?: () => void;
}
```

**Features:**
- Error icon
- Error message
- Retry button
- Support link

#### 7.16 Empty State
**Use Cases:**
- No connection history
- No notifications
- No servers available

**Design:**
- Illustration
- Helpful message
- Call-to-action button

---

## 8. VPN Connection UI Requirements

### Connection Flow

#### 8.1 Connection States
```typescript
enum ConnectionState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTING = 'disconnecting',
  ERROR = 'error'
}
```

#### 8.2 Connection Button Design
**Disconnected State:**
- Large circular button
- Gray/neutral color
- "Connect" text
- Shield icon (outline)

**Connecting State:**
- Animated pulse effect
- Blue/accent color
- "Connecting..." text
- Rotating spinner
- Progress indicator (0-100%)

**Connected State:**
- Green color
- "Disconnect" text
- Shield icon (filled)
- Checkmark indicator

**Error State:**
- Red color
- "Retry" text
- Error icon

### Connection Information Display

#### 8.3 Before Connection
```
┌─────────────────────────────┐
│   Your IP: 203.0.113.45     │
│   Location: United States   │
│   Status: Not Protected     │
└─────────────────────────────┘
```

#### 8.4 After Connection
```
┌─────────────────────────────┐
│   VPN IP: 198.51.100.23     │
│   Server: Germany, Berlin   │
│   Status: Protected ✓       │
│   Duration: 00:15:32        │
└─────────────────────────────┘
```

### Real-time Monitoring

#### 8.5 Bandwidth Display
```
Upload:   ↑ 1.2 MB/s
Download: ↓ 5.4 MB/s

Total Uploaded:   45.2 MB
Total Downloaded: 234.8 MB
```

#### 8.6 Connection Quality Indicator
- Excellent (green, 3 bars)
- Good (yellow, 2 bars)
- Poor (red, 1 bar)

### WireGuard Configuration

#### 8.7 Config Generation
**API Endpoint:** `POST /api/v1/vpn/config`

**Request:**
```typescript
{
  server_id: string;
}
```

**Response:**
```typescript
{
  interface_address: string;
  dns: string;
  server_public_key: string;
  server_endpoint: string;
  allowed_ips: string;
  preshared_key: string;
  config_id: string;
  signature: string;
}
```

#### 8.8 Native VPN Integration
**iOS:** Use `NetworkExtension` framework
**Android:** Use `VpnService` API

**Libraries:**
- `react-native-wireguard` (if available)
- Custom native modules (if needed)

---

## 9. UX and Design Guidelines

### Design Principles

#### 9.1 Visual Hierarchy
- Primary action (Connect button) should be most prominent
- Server list should be easily scannable
- Important information (IP, status) should be immediately visible

#### 9.2 Color Scheme

**Light Theme:**
```typescript
{
  primary: '#2196F3',      // Blue
  secondary: '#4CAF50',    // Green
  error: '#F44336',        // Red
  warning: '#FF9800',      // Orange
  background: '#FFFFFF',
  surface: '#F5F5F5',
  text: '#212121',
  textSecondary: '#757575'
}
```

**Dark Theme:**
```typescript
{
  primary: '#64B5F6',
  secondary: '#81C784',
  error: '#EF5350',
  warning: '#FFB74D',
  background: '#121212',
  surface: '#1E1E1E',
  text: '#FFFFFF',
  textSecondary: '#B0B0B0'
}
```

#### 9.3 Typography
```typescript
{
  h1: { fontSize: 32, fontWeight: 'bold' },
  h2: { fontSize: 24, fontWeight: 'bold' },
  h3: { fontSize: 20, fontWeight: '600' },
  body1: { fontSize: 16, fontWeight: 'normal' },
  body2: { fontSize: 14, fontWeight: 'normal' },
  caption: { fontSize: 12, fontWeight: 'normal' },
  button: { fontSize: 16, fontWeight: '600' }
}
```

#### 9.4 Spacing System
```typescript
{
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
}
```

#### 9.5 Border Radius
```typescript
{
  small: 4,
  medium: 8,
  large: 16,
  round: 999
}
```

### Responsive Design

#### 9.6 Touch Targets
- Minimum touch target: 44x44 points (iOS), 48x48 dp (Android)
- Spacing between touch targets: 8dp minimum

#### 9.7 Screen Sizes
- Small phones: 320-375px width
- Medium phones: 375-414px width
- Large phones: 414-480px width
- Tablets: 768px+ width

### Animations

#### 9.8 Animation Timing
```typescript
{
  fast: 150,      // Quick feedback
  normal: 300,    // Standard transitions
  slow: 500       // Emphasis animations
}
```

#### 9.9 Animation Types
- **Fade:** Screen transitions
- **Slide:** Drawer, modals
- **Scale:** Button press feedback
- **Rotate:** Loading spinners
- **Pulse:** Connection button

### Accessibility

#### 9.10 Requirements
- All interactive elements must have accessible labels
- Minimum contrast ratio: 4.5:1 for text
- Support for screen readers
- Support for dynamic font sizes
- Keyboard navigation support (Android TV)

---

## 10. Animation and Interaction Libraries

### React Native Reanimated
**Use For:**
- Smooth 60fps animations
- Gesture-based interactions
- Complex animation sequences
- Shared element transitions

**Examples:**
```typescript
// Connection button pulse animation
const scale = useSharedValue(1);

useEffect(() => {
  if (isConnecting) {
    scale.value = withRepeat(
      withSequence(
        withTiming(1.1, { duration: 500 }),
        withTiming(1, { duration: 500 })
      ),
      -1
    );
  }
}, [isConnecting]);
```

### React Native Gesture Handler
**Use For:**
- Swipe gestures (server list)
- Pull-to-refresh
- Drawer navigation
- Long press actions

### Lottie Animations
**Use For:**
- Loading animations
- Success/error animations
- Empty state illustrations
- Onboarding animations

**Assets Needed:**
- connecting.json (VPN connecting animation)
- connected.json (success checkmark)
- error.json (error state)
- empty-state.json (no data illustration)

---

## 11. Performance Optimization

### Code Optimization

#### 11.1 Memoization
```typescript
// Memoize expensive computations
const sortedServers = useMemo(() => {
  return servers.sort((a, b) => a.loadPercent - b.loadPercent);
}, [servers]);

// Memoize callbacks
const handleConnect = useCallback((serverId: string) => {
  connectToServer(serverId);
}, []);
```

#### 11.2 List Rendering
```typescript
// Use FlashList for better performance
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={servers}
  renderItem={({ item }) => <ServerCard server={item} />}
  estimatedItemSize={100}
  keyExtractor={(item) => item.id}
/>
```

#### 11.3 Image Optimization
```typescript
// Use FastImage for better caching
import FastImage from 'react-native-fast-image';

<FastImage
  source={{ uri: flagUrl, priority: FastImage.priority.normal }}
  style={{ width: 40, height: 30 }}
  resizeMode={FastImage.resizeMode.contain}
/>
```

### Bundle Optimization

#### 11.4 Code Splitting
```typescript
// Lazy load screens
const PremiumScreen = lazy(() => import('./screens/premium/PremiumScreen'));
const ReferralScreen = lazy(() => import('./screens/premium/ReferralScreen'));
```

#### 11.5 Asset Optimization
- Use WebP format for images
- Compress images (TinyPNG)
- Use SVG for icons
- Lazy load non-critical assets

### Network Optimization

#### 11.6 API Caching
```typescript
// React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false
    }
  }
});
```

#### 11.7 Request Batching
- Batch multiple API calls when possible
- Use GraphQL or custom batch endpoint
- Debounce search queries

### Memory Management

#### 11.8 Cleanup
```typescript
useEffect(() => {
  const subscription = vpnService.onStatusChange((status) => {
    setConnectionStatus(status);
  });
  
  return () => {
    subscription.unsubscribe(); // Cleanup
  };
}, []);
```

#### 11.9 Avoid Memory Leaks
- Clear timers and intervals
- Unsubscribe from event listeners
- Cancel pending API requests on unmount

---

## 12. Security Best Practices

### Token Storage

#### 12.1 Secure Storage
```typescript
// Use Expo SecureStore for tokens
import * as SecureStore from 'expo-secure-store';

// Store tokens
await SecureStore.setItemAsync('access_token', token);
await SecureStore.setItemAsync('refresh_token', refreshToken);

// Retrieve tokens
const token = await SecureStore.getItemAsync('access_token');
```

#### 12.2 Token Refresh
```typescript
// Automatic token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = await SecureStore.getItemAsync('refresh_token');
      const newToken = await refreshAccessToken(refreshToken);
      
      // Retry original request
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### API Security

#### 12.3 Request Headers
```typescript
// Always include required headers
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'X-Device-ID': deviceId,
  'Content-Type': 'application/json'
};
```

#### 12.4 Certificate Pinning
```typescript
// For production, implement SSL pinning
// Prevents man-in-the-middle attacks
```

### Input Validation

#### 12.5 Client-Side Validation
```typescript
// Zod schema for login
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters')
});
```

#### 12.6 Sanitization
```typescript
// Sanitize user inputs
const sanitizeInput = (input: string) => {
  return input.trim().replace(/[<>]/g, '');
};
```

### Data Protection

#### 12.7 Sensitive Data
- Never log sensitive data (passwords, tokens)
- Clear sensitive data from memory after use
- Use secure keyboard for password inputs

#### 12.8 Biometric Authentication
```typescript
// Optional: Add biometric login
import * as LocalAuthentication from 'expo-local-authentication';

const authenticateWithBiometrics = async () => {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Authenticate to access VPN',
    fallbackLabel: 'Use passcode'
  });
  
  return result.success;
};
```

---

## 13. Testing Strategy

### Unit Testing

#### 13.1 Jest Configuration
```json
{
  "preset": "jest-expo",
  "transformIgnorePatterns": [
    "node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)"
  ]
}
```

#### 13.2 Component Testing
```typescript
// Example: ServerCard.test.tsx
import { render, fireEvent } from '@testing-library/react-native';
import ServerCard from './ServerCard';

describe('ServerCard', () => {
  it('renders server information correctly', () => {
    const server = {
      id: '1',
      country: 'United States',
      city: 'New York',
      loadPercent: 45,
      isPremium: false
    };
    
    const { getByText } = render(<ServerCard server={server} />);
    
    expect(getByText('United States')).toBeTruthy();
    expect(getByText('New York')).toBeTruthy();
  });
  
  it('calls onConnect when connect button is pressed', () => {
    const onConnect = jest.fn();
    const { getByText } = render(
      <ServerCard server={mockServer} onConnect={onConnect} />
    );
    
    fireEvent.press(getByText('Connect'));
    expect(onConnect).toHaveBeenCalled();
  });
});
```

### Integration Testing

#### 13.3 API Integration Tests
```typescript
// Test API service
describe('VPN API', () => {
  it('fetches server list successfully', async () => {
    const servers = await vpnApi.getServers();
    expect(servers).toBeInstanceOf(Array);
    expect(servers[0]).toHaveProperty('country');
  });
});
```

### End-to-End Testing

#### 13.4 Detox Configuration
```json
{
  "testRunner": "jest",
  "runnerConfig": "e2e/config.json",
  "configurations": {
    "ios.sim.debug": {
      "device": {
        "type": "iPhone 14"
      },
      "app": "ios.debug"
    },
    "android.emu.debug": {
      "device": {
        "avdName": "Pixel_5_API_31"
      },
      "app": "android.debug"
    }
  }
}
```

#### 13.5 E2E Test Example
```typescript
// e2e/login.test.ts
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });
  
  it('should login successfully', async () => {
    await element(by.id('email-input')).typeText('user@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();
    
    await expect(element(by.id('home-screen'))).toBeVisible();
  });
});
```

### Testing Checklist
- [ ] Unit tests for utilities and helpers
- [ ] Component tests for all UI components
- [ ] Integration tests for API services
- [ ] E2E tests for critical user flows
- [ ] Snapshot tests for UI consistency
- [ ] Performance tests for list rendering
- [ ] Accessibility tests

---

## 14. Deployment and Build

### Development Build

#### 14.1 Expo Development Client
```bash
# Install development client
npx expo install expo-dev-client

# Start development server
npx expo start --dev-client

# Build development client
eas build --profile development --platform ios
eas build --profile development --platform android
```

### Production Build

#### 14.2 EAS Build Configuration
```json
// eas.json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      },
      "ios": {
        "autoIncrement": true
      }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./service-account.json",
        "track": "internal"
      },
      "ios": {
        "appleId": "your-apple-id@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCD123456"
      }
    }
  }
}
```

#### 14.3 Build Commands
```bash
# Android APK (for testing)
eas build --platform android --profile preview

# Android App Bundle (for Play Store)
eas build --platform android --profile production

# iOS (for App Store)
eas build --platform ios --profile production

# Build both platforms
eas build --platform all --profile production
```

### App Store Submission

#### 14.4 iOS App Store
```bash
# Submit to App Store
eas submit --platform ios --latest

# Or manually upload via Xcode
```

**Requirements:**
- Apple Developer Account ($99/year)
- App Store Connect setup
- Privacy policy URL
- App screenshots (all device sizes)
- App description and keywords
- App icon (1024x1024)

#### 14.5 Google Play Store
```bash
# Submit to Play Store
eas submit --platform android --latest
```

**Requirements:**
- Google Play Developer Account ($25 one-time)
- Play Console setup
- Privacy policy URL
- App screenshots (phone, tablet, TV)
- Feature graphic (1024x500)
- App description
- Content rating questionnaire

### Over-The-Air (OTA) Updates

#### 14.6 EAS Update
```bash
# Publish update
eas update --branch production --message "Bug fixes and improvements"

# Configure auto-updates
```

```typescript
// app.json
{
  "expo": {
    "updates": {
      "enabled": true,
      "checkAutomatically": "ON_LOAD",
      "fallbackToCacheTimeout": 0
    }
  }
}
```

### Environment Configuration

#### 14.7 Environment Variables
```typescript
// app.config.ts
export default {
  expo: {
    extra: {
      apiUrl: process.env.API_URL || 'https://api.yourdomain.com',
      environment: process.env.ENVIRONMENT || 'production'
    }
  }
};

// Access in app
import Constants from 'expo-constants';
const API_URL = Constants.expoConfig?.extra?.apiUrl;
```

---

## 15. API Integration Guide

### API Client Setup

#### 15.1 Axios Configuration
```typescript
// services/api/client.ts
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL } from '@/utils/constants';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('access_token');
    const deviceId = await SecureStore.getItemAsync('device_id');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (deviceId) {
      config.headers['X-Device-ID'] = deviceId;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const { access_token } = response.data;
        await SecureStore.setItemAsync('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Logout user
        await SecureStore.deleteItemAsync('access_token');
        await SecureStore.deleteItemAsync('refresh_token');
        // Navigate to login
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### API Service Modules

#### 15.2 Auth Service
```typescript
// services/api/auth.ts
import apiClient from './client';

export const authApi = {
  login: async (email: string, password: string, deviceId: string) => {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
      device_id: deviceId
    });
    return response.data;
  },
  
  register: async (email: string, password: string, deviceId: string) => {
    const response = await apiClient.post('/api/v1/auth/register', {
      email,
      password,
      device_id: deviceId
    });
    return response.data;
  },
  
  logout: async (refreshToken: string) => {
    await apiClient.post('/api/v1/auth/logout', {
      refresh_token: refreshToken
    });
  },
  
  requestPasswordReset: async (email: string) => {
    await apiClient.post('/api/v1/email/request-password-reset', {
      email
    });
  },
  
  resetPassword: async (token: string, newPassword: string) => {
    await apiClient.post('/api/v1/email/reset-password', {
      token,
      new_password: newPassword
    });
  }
};
```

#### 15.3 VPN Service
```typescript
// services/api/vpn.ts
import apiClient from './client';

export const vpnApi = {
  getServers: async () => {
    const response = await apiClient.get('/api/v1/vpn/servers');
    return response.data.servers;
  },
  
  getConfig: async (serverId: string) => {
    const response = await apiClient.post('/api/v1/vpn/config', {
      server_id: serverId
    });
    return response.data;
  },
  
  revokeConfig: async (configId: string) => {
    await apiClient.delete(`/api/v1/vpn/config/${configId}`);
  },
  
  getStats: async () => {
    const response = await apiClient.get('/api/v1/vpn/stats');
    return response.data;
  }
};
```

#### 15.4 User Service
```typescript
// services/api/user.ts
import apiClient from './client';

export const userApi = {
  getProfile: async () => {
    const response = await apiClient.get('/api/v1/users/me');
    return response.data;
  },
  
  updateProfile: async (data: Partial<User>) => {
    const response = await apiClient.patch('/api/v1/users/me', data);
    return response.data;
  },
  
  changePassword: async (currentPassword: string, newPassword: string) => {
    await apiClient.post('/api/v1/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  },
  
  getDevices: async () => {
    const response = await apiClient.get('/api/v1/users/devices');
    return response.data.devices;
  }
};
```

### React Query Integration

#### 15.5 Query Hooks
```typescript
// hooks/useServers.ts
import { useQuery } from 'react-query';
import { vpnApi } from '@/services/api/vpn';

export const useServers = () => {
  return useQuery('servers', vpnApi.getServers, {
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000 // Refetch every 30 seconds
  });
};

// Usage in component
const { data: servers, isLoading, error, refetch } = useServers();
```

#### 15.6 Mutation Hooks
```typescript
// hooks/useVPNConnection.ts
import { useMutation, useQueryClient } from 'react-query';
import { vpnApi } from '@/services/api/vpn';

export const useVPNConnection = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    (serverId: string) => vpnApi.getConfig(serverId),
    {
      onSuccess: (data) => {
        // Invalidate stats query
        queryClient.invalidateQueries('vpn-stats');
      },
      onError: (error) => {
        console.error('Connection failed:', error);
      }
    }
  );
};

// Usage
const { mutate: connect, isLoading } = useVPNConnection();
connect(serverId);
```

---

## 16. State Management with Zustand

### Store Structure

#### 16.1 Auth Store
```typescript
// store/authStore.ts
import create from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  accessToken: null,
  refreshToken: null,
  
  login: async (email, password) => {
    const deviceId = await getDeviceId();
    const response = await authApi.login(email, password, deviceId);
    
    await SecureStore.setItemAsync('access_token', response.access_token);
    await SecureStore.setItemAsync('refresh_token', response.refresh_token);
    
    set({
      isAuthenticated: true,
      accessToken: response.access_token,
      refreshToken: response.refresh_token
    });
  },
  
  logout: async () => {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    
    set({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null
    });
  },
  
  setUser: (user) => set({ user }),
  
  checkAuth: async () => {
    const token = await SecureStore.getItemAsync('access_token');
    set({ isAuthenticated: !!token, accessToken: token });
  }
}));
```

#### 16.2 VPN Store
```typescript
// store/vpnStore.ts
import create from 'zustand';

interface VPNState {
  connectionState: ConnectionState;
  connectedServer: Server | null;
  uploadSpeed: number;
  downloadSpeed: number;
  totalUploaded: number;
  totalDownloaded: number;
  connectionDuration: number;
  
  connect: (server: Server) => Promise<void>;
  disconnect: () => Promise<void>;
  updateStats: (stats: BandwidthStats) => void;
}

export const useVPNStore = create<VPNState>((set, get) => ({
  connectionState: ConnectionState.DISCONNECTED,
  connectedServer: null,
  uploadSpeed: 0,
  downloadSpeed: 0,
  totalUploaded: 0,
  totalDownloaded: 0,
  connectionDuration: 0,
  
  connect: async (server) => {
    set({ connectionState: ConnectionState.CONNECTING });
    
    try {
      const config = await vpnApi.getConfig(server.id);
      await vpnService.connect(config);
      
      set({
        connectionState: ConnectionState.CONNECTED,
        connectedServer: server
      });
    } catch (error) {
      set({ connectionState: ConnectionState.ERROR });
      throw error;
    }
  },
  
  disconnect: async () => {
    set({ connectionState: ConnectionState.DISCONNECTING });
    
    try {
      await vpnService.disconnect();
      
      set({
        connectionState: ConnectionState.DISCONNECTED,
        connectedServer: null,
        uploadSpeed: 0,
        downloadSpeed: 0
      });
    } catch (error) {
      console.error('Disconnect failed:', error);
    }
  },
  
  updateStats: (stats) => {
    set({
      uploadSpeed: stats.uploadSpeed,
      downloadSpeed: stats.downloadSpeed,
      totalUploaded: stats.totalUploaded,
      totalDownloaded: stats.totalDownloaded
    });
  }
}));
```

---

## 17. TypeScript Types

### API Types
```typescript
// types/api.ts
export interface LoginRequest {
  email: string;
  password: string;
  device_id: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface Server {
  id: string;
  country: string;
  country_code: string;
  city: string;
  endpoint: string;
  public_key: string;
  is_active: boolean;
  is_premium: boolean;
  load_percent: number;
}

export interface VPNConfig {
  interface_address: string;
  dns: string;
  server_public_key: string;
  server_endpoint: string;
  allowed_ips: string;
  preshared_key: string;
  config_id: string;
  signature: string;
}

export interface User {
  id: string;
  email: string;
  role: 'user' | 'admin' | 'superadmin';
  is_active: boolean;
  is_premium: boolean;
  bandwidth_limit: number | null;
  created_at: string;
}

export interface BandwidthStats {
  uploadSpeed: number;
  downloadSpeed: number;
  totalUploaded: number;
  totalDownloaded: number;
}
```

---

## 18. Final Checklist

### Development Phase
- [ ] Set up React Native project with Expo
- [ ] Configure TypeScript
- [ ] Set up navigation structure
- [ ] Implement authentication flow
- [ ] Create reusable UI components
- [ ] Integrate with backend API
- [ ] Implement VPN connection logic
- [ ] Add state management
- [ ] Implement all screens
- [ ] Add animations and transitions
- [ ] Implement dark mode
- [ ] Add error handling
- [ ] Add loading states

### Testing Phase
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Perform E2E testing
- [ ] Test on multiple devices
- [ ] Test on different OS versions
- [ ] Performance testing
- [ ] Security audit
- [ ] Accessibility testing

### Pre-Launch Phase
- [ ] Optimize bundle size
- [ ] Optimize images and assets
- [ ] Set up crash reporting (Sentry)
- [ ] Set up analytics
- [ ] Create app store assets
- [ ] Write privacy policy
- [ ] Write terms of service
- [ ] Prepare app store descriptions
- [ ] Beta testing (TestFlight/Play Console)

### Launch Phase
- [ ] Submit to App Store
- [ ] Submit to Play Store
- [ ] Set up OTA updates
- [ ] Monitor crash reports
- [ ] Monitor user feedback
- [ ] Plan post-launch updates

---

## 19. Recommended Tools & Services

### Development Tools
- **VS Code** with React Native extensions
- **React Native Debugger**
- **Flipper** for debugging
- **Reactotron** for state inspection

### Monitoring & Analytics
- **Sentry** - Error tracking
- **Firebase Analytics** - User analytics
- **Firebase Crashlytics** - Crash reporting
- **Mixpanel** - Advanced analytics

### CI/CD
- **GitHub Actions** - Automated builds
- **EAS Build** - Cloud builds
- **Fastlane** - Deployment automation

### Design Tools
- **Figma** - UI/UX design
- **Zeplin** - Design handoff
- **LottieFiles** - Animations

---

## 20. Support & Maintenance

### Post-Launch Maintenance
- Monitor crash reports daily
- Respond to user reviews
- Release bug fixes within 48 hours
- Monthly feature updates
- Quarterly major updates

### Performance Monitoring
- Track app startup time
- Monitor API response times
- Track crash-free rate (target: >99.5%)
- Monitor battery usage
- Track data usage

### User Feedback
- In-app feedback form
- App store reviews monitoring
- Support email
- Community forum (optional)

---

## Conclusion

This frontend documentation provides a complete blueprint for building a production-ready VPN mobile application using React Native. Follow these guidelines to create a fast, secure, and user-friendly mobile experience that seamlessly integrates with your FastAPI backend.

**Key Success Factors:**
- Clean, maintainable code architecture
- Smooth, responsive UI/UX
- Robust error handling
- Comprehensive testing
- Security-first approach
- Performance optimization
- Regular updates and maintenance

**Next Steps:**
1. Review this documentation with your team
2. Set up development environment
3. Create project timeline
4. Begin implementation following the structure outlined
5. Iterate based on user feedback

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-03-08  
**Maintained By:** Development Team
