# Diagram Style Guide

## Canvas
- **Grid**: 10 px spacing with snap enabled
- **Page Size**: A4 (210×297mm) for print, 1920×1080 for slides
- **Background**: Neutral white (#FFFFFF) or light gray (#F8F9FA)

## Typography
- **Primary Font**: Inter or system sans-serif
- **Font Sizes**:
  - Title: 20–24 pt
  - Section Headers: 16–18 pt
  - Body Text: 12–14 pt
  - Annotations: 11–12 pt
- **Font Weights**:
  - Titles: 600 (semibold)
  - Headers: 500 (medium)
  - Body: 400 (regular)
  - Annotations: 300 (light)

## Lines & Connectors
- **Connector Type**: Orthogonal (90-degree angles)
- **Arrowheads**: Solid arrowheads on flow direction
- **Stroke Width**: 1–2 px for primary flows, 0.5–1 px for secondary
- **Opacity**: 50–60% for secondary/background flows
- **Color**: #2D3748 (gray-800) for primary, #718096 (gray-500) for secondary

## Shapes
- **Corner Radius**: 6–8 px for rounded corners
- **Padding**: 8–12 px internal padding
- **Stroke**: 1–2 px border width
- **Label Placement**: Outside vendor icons, inside generic blocks
- **Shadow**: Subtle drop shadow (2px offset, 4px blur, 10% opacity)

## Colors
- **Primary Palette**:
  - Primary: #3182CE (blue-600)
  - Secondary: #38A169 (green-600)
  - Accent: #D69E2E (yellow-600)
  - Danger: #E53E3E (red-600)
- **Neutral Palette**:
  - Background: #FFFFFF
  - Surface: #F7FAFC
  - Border: #E2E8F0
  - Text: #2D3748
- **Vendor Colors**: Do not recolor official vendor icons

## Icons & Symbols
- **Vendor Icons**: Use official colors and proportions
- **Scale Range**: 0.75–1.25x original size
- **Alignment**: Center-aligned within containers
- **Spacing**: 4–8 px margin around icons

## Layout & Spacing
- **Grid Alignment**: Snap to 10 px grid
- **Element Spacing**: 20–40 px between major elements
- **Group Spacing**: 10–20 px within groups
- **Consistent Margins**: 16 px standard margin

## Export Settings
- **Source Format**: .drawio (editable XML)
- **Vector Format**: .svg for web and presentations
- **Print Format**: .pdf for documentation
- **Image Format**: .png for quick sharing (300 DPI)
- **Color Mode**: RGB for digital, CMYK for print

## BPMN Specific Rules
- **Swimlanes**: 120 px width for roles, 200 px for systems
- **Events**: 36×36 px circles
- **Gateways**: 40×40 px diamonds
- **Tasks**: 100×60 px rectangles
- **Connectors**: Flow from center of elements

## Cloud Architecture Rules
- **Service Icons**: Official vendor icons only
- **Region Tags**: Bottom-right corner, 10 pt font
- **Environment Tags**: Top-right corner, 10 pt font
- **Network Lines**: Dashed for external, solid for internal
- **Trust Boundaries**: Dotted lines with labels

## Accessibility
- **Color Contrast**: Minimum 4.5:1 for text
- **Text Size**: Minimum 12 pt for readability
- **Alt Text**: Include descriptive alt text for all images
- **Keyboard Navigation**: Logical reading order

## Quality Checklist
- [ ] Grid alignment verified
- [ ] Font consistency checked
- [ ] Color palette applied
- [ ] Vendor icons not recolored
- [ ] Labels properly placed
- [ ] Export formats generated
- [ ] Accessibility requirements met
- [ ] File naming convention followed
