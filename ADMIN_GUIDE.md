# Admin Product Management - User Guide

## Overview

The admin product management system provides a complete CRUD (Create, Read, Update, Delete) interface for managing products in the Halltek Paints application.

## Features

### ✨ Key Capabilities

- **Add Products**: Create new products with images, descriptions, pricing, and custom fonts
- **Edit Products**: Update existing product information
- **Delete Products**: Remove products from the database
- **Image Upload**: Upload product images with drag-and-drop support
- **Font Customization**: Choose from preset fonts or upload custom font files
- **Real-time Preview**: See image and font previews before saving

## Accessing the Admin Page

1. Start the Flask server:

   ```bash
   python app.py
   ```

2. Navigate to: `http://127.0.0.1:5000/admin/product.html`

## Using the Interface

### Adding a New Product

1. Click the **"Add New Product"** button in the top right
2. Fill in the required fields:
   - **Product Name** (required)
   - **Price** (required)
   - **Description** (optional)
3. Upload an image:
   - Click the upload area or drag and drop an image
   - Supported formats: PNG, JPG, JPEG, GIF, WEBP
   - Preview will appear below the upload area
4. Select a font family from the dropdown
   - Preview updates in real-time
5. Optionally upload a custom font file (TTF, OTF, WOFF, WOFF2)
6. Click **"Save Product"**

### Editing a Product

1. Find the product card you want to edit
2. Click the **"Edit"** button
3. Modify the fields as needed
4. Click **"Save Product"**

### Deleting a Product

1. Find the product card you want to delete
2. Click the **"Delete"** button
3. Confirm the deletion in the popup dialog

## Keyboard Shortcuts

- **Ctrl/Cmd + N**: Open "Add New Product" modal
- **ESC**: Close the modal

## API Endpoints

The system uses the following REST API endpoints:

- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get single product
- `POST /api/products` - Create new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

## File Structure

```
halltekpaints/
├── templates/
│   └── admin/
│       └── product.html          # Admin interface
├── Static/
│   ├── css/
│   │   └── admin.css            # Admin styles
│   ├── js/
│   │   └── admin.js             # Admin JavaScript
│   └── uploads/
│       └── products/            # Uploaded product images
│           └── fonts/           # Uploaded custom fonts
└── app.py                       # Flask backend with CRUD routes
```

## Technical Details

### Database Schema

Products are stored in MongoDB with the following structure:

```javascript
{
  _id: ObjectId,
  name: String,
  price: Number,
  description: String,
  image: String,              // URL to uploaded image
  font_family: String,        // Font family name
  custom_font: String         // URL to custom font file
}
```

### Image Upload

- Images are stored in: `Static/uploads/products/`
- Filenames are prefixed with timestamps to prevent conflicts
- Only allowed extensions: png, jpg, jpeg, gif, webp

### Font Upload

- Custom fonts are stored in: `Static/uploads/products/fonts/`
- Supported formats: TTF, OTF, WOFF, WOFF2

## Troubleshooting

### Jinja2 Template Showing as Plain Text

**Problem**: The page shows `{% %}` blocks as text instead of rendering them.

**Solution**: Make sure you're accessing the page through Flask at `http://127.0.0.1:5000/admin/product.html`, not opening the HTML file directly.

### Images Not Uploading

**Problem**: Images don't appear after upload.

**Solution**:

1. Check that the `Static/uploads/products/` directory exists
2. Verify file permissions
3. Check browser console for errors

### MongoDB Connection Errors

**Problem**: "Database connection error" messages.

**Solution**:

1. Ensure MongoDB is running
2. Check the connection string in `app.py`
3. Verify database name is correct

## Design Features

- **Modern UI**: Gradient backgrounds, smooth animations, and glassmorphism effects
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Flash Messages**: Real-time feedback for all operations
- **Empty State**: Helpful message when no products exist
- **Loading States**: Visual feedback during operations
- **Error Handling**: Graceful error messages for failed operations

## Security Considerations

- File upload validation (type and extension checking)
- Secure filename handling
- MongoDB injection protection through parameterized queries
- CORS headers configured for development

## Future Enhancements

Potential improvements:

- Image cropping/resizing
- Bulk product import/export
- Product categories
- Search and filtering
- Pagination for large product lists
- Product variants (sizes, colors)
- Stock management
- Product analytics
