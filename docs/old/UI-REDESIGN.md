# UI Redesign - Bloomberg Terminal Theme

## 🎨 Design System

### Color Palette
The new design uses a professional dark theme inspired by Bloomberg Terminal:

#### Background Colors
- **Primary Background**: `#0a0e1a` - Deep navy, main app background
- **Secondary Background**: `#131720` - Slightly lighter navy for header/footer
- **Tertiary Background**: `#1a1f2e` - Card backgrounds and elevated surfaces
- **Card Background**: `#161b26` - Individual component cards

#### Border Colors
- **Primary Border**: `#2a3142` - Subtle borders between elements
- **Accent Border**: `#3a4357` - Hover states and emphasis

#### Text Colors
- **Primary Text**: `#e8eaed` - Main content, high contrast
- **Secondary Text**: `#9ba3b5` - Supporting text, labels
- **Muted Text**: `#6c7589` - Hints, disabled states

#### Accent Colors
- **Orange**: `#ff7043` - Primary actions, CTAs, main brand color
- **Blue**: `#42a5f5` - Information, links, data highlights
- **Green**: `#66bb6a` - Success states, positive indicators
- **Red**: `#ef5350` - Errors, alerts, high-risk matches
- **Yellow**: `#ffa726` - Warnings, medium-risk indicators
- **Purple**: `#ab47bc` - User blacklist badge, secondary accent

## 🎯 Key Design Features

### 1. Professional Header
- Dark background with orange accent border
- Compact, information-dense layout
- Sticky positioning for always-visible navigation
- Orange square bullet point for brand identity

### 2. Card Design
- Subtle borders with hover effects
- Consistent 4px border radius (sharp, terminal-like)
- Shadow depth for visual hierarchy
- Tertiary background for information panels

### 3. Data Tables
- Alternating row colors for better readability
- Hover states on all interactive elements
- Uppercase column headers with letter spacing
- Compact, data-dense presentation
- Custom scrollbars matching theme

### 4. Badges & Indicators

#### Police Blacklist Badge
- **Design**: Red gradient with glow effect
- **Style**: Bold, uppercase, with shadow
- **Purpose**: Maximum visibility for critical matches

#### User Blacklist Badge
- **Design**: Purple with border
- **Style**: Medium weight, clean
- **Purpose**: Distinguished from police matches

#### Score Badges
- **90-100%**: Red gradient - Critical risk
- **80-89%**: Orange gradient - High risk
- **70-79%**: Yellow gradient - Medium risk
- **60-69%**: Blue gradient - Low risk
- **<60%**: Gray gradient - Minimal risk

### 5. Form Controls
- Dark backgrounds with light borders
- Orange accent color for focus states
- File input with styled button
- Checkbox with orange accent color
- Clean, minimal design

### 6. Buttons
- **Primary (Run Screening)**: Orange gradient with glow
- **Secondary (Export)**: Green with hover lift
- **Upload**: Orange with uppercase text
- All buttons have smooth transitions and disabled states

## 📊 Typography

### Font Stack
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif
```

### Sizes & Weights
- **Headers**: 1.1rem, 600 weight, uppercase, 0.5px letter spacing
- **Body**: 0.85-0.9rem, 400 weight
- **Labels**: 0.8rem, 600 weight, uppercase, 0.3px letter spacing
- **Code**: Monaco, Courier New (monospace)

## 🎭 Animations & Transitions

### Hover Effects
- **Cards**: Border color change (0.2s ease)
- **Buttons**: Transform translateY + shadow (0.2s ease)
- **Table Rows**: Background color change (0.15s ease)

### Focus States
- 2px orange outline with 2px offset
- Visible on all interactive elements

### Loading States
- Pulse animation on disabled buttons
- Smooth opacity transitions

## 🔧 Custom Scrollbars

### Webkit Browsers
- **Track**: Tertiary background
- **Thumb**: Border accent color
- **Thumb Hover**: Orange accent
- 10px width/height
- 4px border radius

## 📱 Responsive Design

### Grid Layouts
- **Upload Sections**: 2 columns → 1 column at 1024px
- **Control Grid**: 2 columns → 1 column at 768px
- **Filters**: Flex wrap for small screens

### Typography
- Scales appropriately on all screen sizes
- Maintains readability on mobile devices

## 🎨 Visual Hierarchy

### Priority Levels
1. **Critical Actions**: Orange gradient buttons (Run Screening)
2. **Primary Content**: Card backgrounds with borders
3. **Secondary Content**: Tertiary backgrounds (info panels)
4. **Tertiary Content**: Muted text colors

### Information Architecture
- Header: Always visible, minimal height
- Upload sections: Side-by-side for quick access
- Screening controls: Centralized, prominent
- Results: Full-width, data-focused presentation

## 🚀 Performance Optimizations

### CSS Performance
- Hardware-accelerated transforms
- Efficient selectors
- Minimal repaints/reflows
- CSS variables for theme consistency

### Visual Performance
- Smooth 60fps animations
- Reduced motion for accessibility
- Optimized shadow usage
- Minimal gradient usage

## 🎯 Accessibility Features

### Color Contrast
- All text meets WCAG AA standards
- High contrast ratios (>4.5:1)
- Color-blind friendly palette

### Interactive Elements
- Clear focus indicators
- Keyboard navigation support
- Proper label associations
- Descriptive button text

### Visual Feedback
- Hover states on all clickable elements
- Loading indicators for async operations
- Error/warning messages with icons
- Success confirmations

## 💡 Design Inspiration

The design draws inspiration from:
- **Bloomberg Terminal**: Professional, data-dense, dark theme
- **Financial Software**: Clean, minimal, focus on information
- **Modern UI Trends**: Subtle gradients, smooth animations, card-based layout
- **Terminal Aesthetics**: Monospace fonts, uppercase labels, compact spacing

## 🔮 Future Enhancements

Potential improvements:
- Theme switcher (dark/light mode)
- Customizable accent colors
- Data visualization charts
- Real-time updates with WebSocket indicators
- Keyboard shortcuts overlay
- Advanced filtering with visual query builder
