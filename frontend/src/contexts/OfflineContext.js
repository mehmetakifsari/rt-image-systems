import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const OfflineContext = createContext(null);

const DB_NAME = 'RTGarantiOfflineDB';
const STORE_NAME = 'pendingUploads';

// IndexedDB helper
const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
  });
};

export const OfflineProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingUploads, setPendingUploads] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);

  // Load pending uploads from IndexedDB
  const loadPendingUploads = useCallback(async () => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.getAll();
      
      request.onsuccess = () => {
        setPendingUploads(request.result || []);
      };
    } catch (error) {
      console.error('Error loading pending uploads:', error);
    }
  }, []);

  // Add to offline queue
  const addToQueue = useCallback(async (uploadData) => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      
      const item = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        ...uploadData,
        status: 'pending',
        createdAt: new Date().toISOString(),
        retryCount: 0
      };
      
      store.add(item);
      
      transaction.oncomplete = () => {
        loadPendingUploads();
      };
      
      return item;
    } catch (error) {
      console.error('Error adding to queue:', error);
      throw error;
    }
  }, [loadPendingUploads]);

  // Remove from queue
  const removeFromQueue = useCallback(async (id) => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.delete(id);
      
      transaction.oncomplete = () => {
        loadPendingUploads();
      };
    } catch (error) {
      console.error('Error removing from queue:', error);
    }
  }, [loadPendingUploads]);

  // Update queue item
  const updateQueueItem = useCallback(async (id, updates) => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      
      const getRequest = store.get(id);
      getRequest.onsuccess = () => {
        const item = getRequest.result;
        if (item) {
          store.put({ ...item, ...updates });
        }
      };
      
      transaction.oncomplete = () => {
        loadPendingUploads();
      };
    } catch (error) {
      console.error('Error updating queue item:', error);
    }
  }, [loadPendingUploads]);

  // Sync pending uploads when online
  const syncPendingUploads = useCallback(async () => {
    if (!isOnline || isSyncing || pendingUploads.length === 0) return;
    
    setIsSyncing(true);
    
    for (const upload of pendingUploads) {
      if (upload.status === 'synced') continue;
      
      try {
        // Attempt to upload
        const formData = new FormData();
        formData.append('file', upload.file);
        formData.append('media_type', upload.mediaType);
        
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/records/${upload.recordId}/upload`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
          }
        );
        
        if (response.ok) {
          await removeFromQueue(upload.id);
        } else {
          await updateQueueItem(upload.id, { 
            retryCount: upload.retryCount + 1,
            lastError: `HTTP ${response.status}`
          });
        }
      } catch (error) {
        await updateQueueItem(upload.id, { 
          retryCount: upload.retryCount + 1,
          lastError: error.message
        });
      }
    }
    
    setIsSyncing(false);
  }, [isOnline, isSyncing, pendingUploads, removeFromQueue, updateQueueItem]);

  // Online/offline event listeners
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      syncPendingUploads();
    };
    
    const handleOffline = () => {
      setIsOnline(false);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    loadPendingUploads();
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [loadPendingUploads, syncPendingUploads]);

  // Auto-sync when online
  useEffect(() => {
    if (isOnline && pendingUploads.length > 0) {
      const timer = setTimeout(syncPendingUploads, 2000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, pendingUploads.length, syncPendingUploads]);

  return (
    <OfflineContext.Provider value={{
      isOnline,
      pendingUploads,
      isSyncing,
      addToQueue,
      removeFromQueue,
      syncPendingUploads
    }}>
      {children}
    </OfflineContext.Provider>
  );
};

export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within OfflineProvider');
  }
  return context;
};
