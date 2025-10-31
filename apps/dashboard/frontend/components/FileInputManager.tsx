'use client'

import React, { useState, useRef, useCallback } from 'react';
import { Upload, Folder, FileText, Search, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadFile, validateFilePath, browseFolder } from '@/lib/api';

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  extension?: string;
  compatible: boolean;
}

interface FileInputManagerProps {
  onFileSelected: (filePath: string, source: 'upload' | 'path' | 'browse') => void;
  onMultipleFilesSelected?: (filePaths: string[]) => void;
  selectedFile?: string;
  className?: string;
  allowMultiple?: boolean;
}

interface UploadProgress {
  filename: string;
  progress: number;
  success: boolean;
  error?: string;
  filePath?: string;
  sizeMb?: number;
}

export default function FileInputManager({ 
  onFileSelected, 
  onMultipleFilesSelected,
  selectedFile, 
  className = '',
  allowMultiple = false
}: FileInputManagerProps) {
  const [activeTab, setActiveTab] = useState<'upload' | 'path' | 'browse'>('upload');
  const [dragOver, setDragOver] = useState(false);
  const [pathInput, setPathInput] = useState('');
  const [pathValidation, setPathValidation] = useState<{ valid: boolean; error?: string; loading: boolean }>({ valid: false, loading: false });
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [uploading, setUploading] = useState(false);
  const [currentPath, setCurrentPath] = useState('/');
  const [folderContents, setFolderContents] = useState<FileItem[]>([]);
  const [browseError, setBrowseError] = useState<string | null>(null);
  const [browseLoading, setBrowseLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle single file upload
  const handleSingleFileUpload = useCallback(async (file: File) => {
    setUploading(true);
    setUploadProgress([{ filename: file.name, progress: 0, success: false }]);
    
    try {
      const result = await uploadFile(file);
      
      if (result.success) {
        setUploadProgress([{ 
          filename: result.filename, 
          progress: 100, 
          success: true,
          filePath: result.file_path
        }]);
        onFileSelected(result.file_path, 'upload');
      } else {
        setUploadProgress([{ 
          filename: file.name, 
          progress: 0, 
          success: false, 
          error: result.error || 'Upload failed' 
        }]);
      }
    } catch (error) {
      setUploadProgress([{ 
        filename: file.name, 
        progress: 0, 
        success: false, 
        error: error instanceof Error ? error.message : 'Upload failed' 
      }]);
    }
    setUploading(false);
  }, [onFileSelected]);

  // Handle multiple file upload
  const handleMultipleFileUpload = useCallback(async (files: File[]) => {
    setUploading(true);
    const initialProgress: UploadProgress[] = files.map(f => ({
      filename: f.name,
      progress: 0,
      success: false
    }));
    setUploadProgress(initialProgress);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const response = await fetch('http://localhost:8000/api/files/upload-multiple', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      const updatedProgress: UploadProgress[] = result.results.map((r: {
        filename: string;
        success: boolean;
        error?: string;
        file_path?: string;
        size_mb?: number;
      }) => ({
        filename: r.filename,
        progress: r.success ? 100 : 0,
        success: r.success,
        error: r.error,
        filePath: r.file_path,
        sizeMb: r.size_mb
      }));
      
      setUploadProgress(updatedProgress);

      // Notify parent with successful uploads
      if (onMultipleFilesSelected && result.successful > 0) {
        const successfulPaths = updatedProgress
          .filter(p => p.success && p.filePath)
          .map(p => p.filePath!);
        onMultipleFilesSelected(successfulPaths);
      }
    } catch {
      const failedProgress: UploadProgress[] = files.map(f => ({
        filename: f.name,
        progress: 0,
        success: false,
        error: 'Upload failed'
      }));
      setUploadProgress(failedProgress);
    }
    setUploading(false);
  }, [onMultipleFilesSelected]);

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      if (files.length === 1 || !onMultipleFilesSelected) {
        await handleSingleFileUpload(files[0]);
      } else {
        await handleMultipleFileUpload(files);
      }
    }
  }, [handleSingleFileUpload, handleMultipleFileUpload, onMultipleFilesSelected]);

  // Handle path input validation
  const handlePathChange = async (path: string) => {
    setPathInput(path);
    
    if (!path.trim()) {
      setPathValidation({ valid: false, loading: false });
      return;
    }

    setPathValidation({ valid: false, loading: true });

    try {
      const result = await validateFilePath(path);
      setPathValidation({ 
        valid: result.valid, 
        error: result.error,
        loading: false 
      });
      
      if (result.valid) {
        onFileSelected(path, 'path');
      }
    } catch {
      setPathValidation({ 
        valid: false, 
        error: 'Failed to validate path', 
        loading: false 
      });
    }
  };

  // Handle folder browsing
  const handleBrowsePath = useCallback(async (path: string) => {
    setBrowseLoading(true);
    setBrowseError(null);
    
    try {
      const result = await browseFolder(path);
      if (result.error) {
        setBrowseError(result.error);
        setFolderContents([]);
      } else {
        setFolderContents(result.files);
      }
    } catch {
      setBrowseError('Failed to browse folder');
      setFolderContents([]);
    }
    
    setBrowseLoading(false);
  }, []);

  const handleFolderClick = (item: FileItem) => {
    if (item.type === 'folder') {
      setCurrentPath(item.path);
      handleBrowsePath(item.path);
    } else if (item.compatible) {
      onFileSelected(item.path, 'browse');
    }
  };

  const navigateToParent = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
    handleBrowsePath(parentPath);
  };

  // Initialize folder browsing on mount
  React.useEffect(() => {
    handleBrowsePath(currentPath);
  }, [currentPath, handleBrowsePath]);

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-2 px-4 text-sm font-medium border-b-2 ${
              activeTab === 'upload'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Upload File
          </button>
          <button
            onClick={() => setActiveTab('path')}
            className={`py-2 px-4 text-sm font-medium border-b-2 ${
              activeTab === 'path'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Enter Path
          </button>
          <button
            onClick={() => setActiveTab('browse')}
            className={`py-2 px-4 text-sm font-medium border-b-2 ${
              activeTab === 'browse'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Folder className="w-4 h-4 inline mr-2" />
            Browse Folder
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'upload' && (
          <div>
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragOver
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-2">
                Drag and drop files here
              </p>
              <p className="text-sm text-gray-600 mb-4">
                or click to browse • Supports files up to 500MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.json,.xlsx,.xls,.tsv,.txt"
                multiple={!!onMultipleFilesSelected}
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  if (files.length === 1 || !onMultipleFilesSelected) {
                    if (files[0]) handleSingleFileUpload(files[0]);
                  } else if (files.length > 1) {
                    handleMultipleFileUpload(files);
                  }
                }}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : onMultipleFilesSelected ? 'Browse Files (Multi-select)' : 'Browse File'}
              </button>
              <p className="text-xs text-gray-500 mt-2">
                Supported: CSV, JSON, Excel, TSV, TXT • Max 500MB per file
              </p>
            </div>
            
            {uploadProgress.length > 0 && (
              <div className="mt-4 space-y-2">
                {uploadProgress.map((file, idx) => (
                  <div key={idx} className={`p-3 rounded border ${
                    file.success 
                      ? 'bg-green-50 border-green-200' 
                      : file.error 
                      ? 'bg-red-50 border-red-200' 
                      : 'bg-blue-50 border-blue-200'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center flex-1 min-w-0">
                        {file.success ? (
                          <CheckCircle className="w-4 h-4 mr-2 text-green-600 shrink-0" />
                        ) : file.error ? (
                          <AlertCircle className="w-4 h-4 mr-2 text-red-600 shrink-0" />
                        ) : (
                          <div className="w-4 h-4 mr-2 border-2 border-blue-600 border-t-transparent rounded-full animate-spin shrink-0" />
                        )}
                        <span className="text-sm font-medium truncate">{file.filename}</span>
                      </div>
                      {file.sizeMb && (
                        <span className="text-xs text-gray-500 ml-2">{file.sizeMb} MB</span>
                      )}
                    </div>
                    {file.error && (
                      <p className="text-xs text-red-700 mt-1 ml-6">{file.error}</p>
                    )}
                    {file.filePath && (
                      <p className="text-xs text-gray-600 mt-1 ml-6 truncate">{file.filePath}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'path' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full File Path
            </label>
            <div className="relative">
              <input
                type="text"
                value={pathInput}
                onChange={(e) => handlePathChange(e.target.value)}
                placeholder="Enter full path to data file (e.g., /path/to/data.csv)"
                className={`w-full border rounded-md px-3 py-2 pr-10 ${
                  pathValidation.valid
                    ? 'border-green-500'
                    : pathValidation.error
                    ? 'border-red-500'
                    : 'border-gray-300'
                }`}
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                {pathValidation.loading && (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                )}
                {pathValidation.valid && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                {pathValidation.error && !pathValidation.loading && (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
              </div>
            </div>
            {pathValidation.error && (
              <p className="mt-2 text-sm text-red-600">{pathValidation.error}</p>
            )}
            <p className="mt-2 text-sm text-gray-600">
              Type the full path to your data file. Supported formats: CSV, JSON, Excel, TSV, TXT
            </p>
          </div>
        )}

        {activeTab === 'browse' && (
          <div>
            <div className="flex items-center mb-4">
              <button
                onClick={navigateToParent}
                disabled={currentPath === '/'}
                className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 mr-2"
              >
                ↑ Parent
              </button>
              <input
                type="text"
                value={currentPath}
                onChange={(e) => setCurrentPath(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleBrowsePath(currentPath)}
                className="flex-1 border border-gray-300 rounded-md px-3 py-2"
                placeholder="Enter folder path"
              />
              <button
                onClick={() => handleBrowsePath(currentPath)}
                disabled={browseLoading}
                className="ml-2 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>

            {browseError && (
              <div className="mb-4 p-3 bg-red-50 text-red-800 rounded flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                {browseError}
              </div>
            )}

            {browseLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading folder contents...</p>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg max-h-64 overflow-y-auto">
                {folderContents.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    No files found in this directory
                  </div>
                ) : (
                  folderContents.map((item, index) => (
                    <div
                      key={index}
                      onClick={() => handleFolderClick(item)}
                      className={`p-3 border-b border-gray-200 last:border-b-0 cursor-pointer hover:bg-gray-50 ${
                        !item.compatible && item.type === 'file' ? 'opacity-50' : ''
                      } ${
                        selectedFile === item.path ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          {item.type === 'folder' ? (
                            <Folder className="w-5 h-5 text-blue-600 mr-3" />
                          ) : (
                            <FileText className="w-5 h-5 text-gray-600 mr-3" />
                          )}
                          <div>
                            <p className="font-medium text-gray-900">{item.name}</p>
                            {item.type === 'file' && item.size && (
                              <p className="text-xs text-gray-500">
                                {(item.size / 1024 / 1024).toFixed(2)} MB
                                {item.extension && ` • ${item.extension}`}
                              </p>
                            )}
                          </div>
                        </div>
                        {item.compatible && item.type === 'file' && (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        )}
                        {item.type === 'folder' && (
                          <span className="text-blue-600 text-sm">→</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}