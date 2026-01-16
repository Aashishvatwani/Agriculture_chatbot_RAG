import { useState, useRef, useEffect } from 'react';
import './ImageFeatures.css';

/**
 * ImageFeatures component
 * - User uploads an image
 * - Pass base64 image data to parent for backend processing
 */
function ImageFeatures({ onImageSelect, selectedImage, disabled = false }) {
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    setImagePreview(selectedImage);
    if (!selectedImage && fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  }, [selectedImage]);

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      alert('Image size should be less than 5MB');
      return;
    }

    try {
      const base64Data = await fileToBase64(file);
      setImagePreview(base64Data);
      // Pass base64 data to parent
      if (onImageSelect) {
        onImageSelect(base64Data);
      }
    } catch (err) {
      console.error('Error reading image:', err);
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const clearImage = () => {
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    // Notify parent image is cleared
    if (onImageSelect) {
      onImageSelect(null);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="image-features">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="image-input-hidden"
        disabled={disabled}
      />

      <button
        type="button"
        className="image-btn"
        onClick={handleButtonClick}
        disabled={disabled}
        title="Upload image for analysis"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <rect
            x="2.5"
            y="3.75"
            width="15"
            height="12.5"
            rx="2"
            stroke="currentColor"
            strokeWidth="1.5"
          />
          <circle
            cx="6.875"
            cy="7.5"
            r="1.25"
            stroke="currentColor"
            strokeWidth="1.25"
          />
          <path
            d="M2.5 13.75L6.25 10L8.75 12.5L12.5 8.75L17.5 13.75"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Preview thumbnails for selected image */}
      {imagePreview && (
        <div className="image-preview-mini">
           <img src={imagePreview} alt="Selected" />
           <button className="preview-mini-close" onClick={clearImage}>×</button>
        </div>
      )}
    </div>
  );
}

export default ImageFeatures;
