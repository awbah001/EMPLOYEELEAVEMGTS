# Document Upload Feature for Leave Applications

## Overview
Staff members can now upload supporting documents when applying for leave. These documents can be reviewed by Department Heads and HR personnel during the approval process.

## Changes Made

### 1. Database Model Updates
**File:** `staffleave/slms/slmsapp/models.py`
- Added `supporting_document` field to `Staff_Leave` model
- Field type: FileField with upload_to='leave_documents/'
- Optional field (null=True, blank=True)
- Added helper method `get_document_filename()` to extract filename from path

### 2. Staff Leave Application Form
**File:** `staffleave/slms/templates/staff/apply_leave.html`
- Updated form to support multipart/form-data encoding
- Added file upload input with:
  - Accepted formats: PDF, DOC, DOCX, JPG, PNG
  - Maximum file size: 5MB
  - Real-time file preview with name and size display
  - Remove file functionality
  - Client-side validation for file type and size
- Updated leave guidelines to mention document upload requirements
- Added JavaScript for:
  - File validation (type and size)
  - File preview display
  - File removal functionality
  - File size formatting

### 3. Leave Application Processing
**File:** `staffleave/slms/slms/staffviews.py`
- Updated `STAFF_APPLY_LEAVE_SAVE` view to handle file uploads
- Added server-side validation:
  - File size check (max 5MB)
  - File extension validation (.pdf, .doc, .docx, .jpg, .jpeg, .png)
  - Error messages for invalid files
- Saves uploaded document with leave application

### 4. HR Approval Interface
**File:** `staffleave/slms/templates/hr/approve_leave.html`
- Added document display in the pending leaves table
- Shows "View Document" link when document is attached
- Link opens document in new tab for review

### 5. HR Rejection Interface
**File:** `staffleave/slms/templates/hr/reject_leave.html`
- Added dedicated section for supporting documents
- Displays document with icon, filename, and download link
- Only shows when document is attached

### 6. Staff Leave History
**File:** `staffleave/slms/templates/staff/leave_history.html`
- Added "Document" column to leave history table
- Shows attachment icon for leaves with documents
- Shows "-" for leaves without documents
- Document links open in new tab

### 7. Database Migration
**Migration:** `0011_staff_leave_supporting_document_and_more.py`
- Adds supporting_document field to staff_leave table
- Applied successfully

## Features

### File Upload Security
- **Server-side validation**: Checks file size and type before saving
- **Client-side validation**: Immediate feedback on invalid files
- **Allowed formats**: PDF, DOC, DOCX, JPG, PNG only
- **Size limit**: 5MB maximum
- **Secure storage**: Files stored in media/leave_documents/ directory

### User Experience
- **Real-time preview**: Shows selected file name and size
- **Easy removal**: One-click file removal before submission
- **Clear guidelines**: Instructions on when documents are required
- **Visual feedback**: Icons and formatting for document status
- **Accessibility**: Documents can be downloaded by authorized users

### Authorization
- **Staff**: Can upload documents with their leave applications
- **Department Heads**: Can view documents when reviewing leaves
- **HR Personnel**: Can view documents when reviewing leaves
- **Documents stored**: In media/leave_documents/ with unique filenames

## Usage Instructions

### For Staff Members
1. Navigate to "Apply for Leave" page
2. Fill in leave details (type, dates, reason)
3. Click "Choose File" under Supporting Document section
4. Select your document (PDF, DOC, DOCX, JPG, or PNG, max 5MB)
5. Preview shows file name and size
6. Click "Submit Application"

### For Department Heads & HR
1. Navigate to leave approval page
2. Click "View Document" link next to leaves with attachments
3. Document opens in new tab for review
4. Make approval/rejection decision based on document and application details

## File Storage
- **Location**: `staffleave/slms/media/leave_documents/`
- **Naming**: Django automatically generates unique filenames to prevent conflicts
- **Access**: Files are served through Django's media URL configuration

## Testing Checklist
- ✅ Upload PDF document with leave application
- ✅ Upload DOC/DOCX document with leave application
- ✅ Upload image (JPG/PNG) with leave application
- ✅ Verify file size validation (>5MB rejected)
- ✅ Verify file type validation (invalid types rejected)
- ✅ View document from HR approval page
- ✅ View document from HR rejection page
- ✅ View document indicator in staff leave history
- ✅ Submit leave application without document (optional)

## Future Enhancements
1. Multiple document uploads per leave application
2. Document preview within the application (PDF viewer)
3. Document download tracking/audit log
4. Automatic document OCR for medical certificates
5. Document expiry tracking (e.g., medical certificates)
6. Thumbnail generation for image documents
7. Document compression for large files

## Technical Notes
- Media files are not version controlled (added to .gitignore)
- Ensure MEDIA_ROOT and MEDIA_URL are properly configured in settings.py
- In production, consider using cloud storage (S3, Azure Blob) for documents
- Implement regular backup of uploaded documents
- Consider adding virus scanning for uploaded files in production

## Support
For any issues or questions regarding document uploads, please contact the system administrator.

---
**Last Updated:** November 21, 2025
**Feature Status:** ✅ Completed and Tested

