import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Bell, X, Check, CheckCheck, AlertTriangle, FileText, Clock } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const NotificationBell = () => {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API}/notifications?limit=10`);
      setNotifications(response.data.notifications);
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await axios.put(`${API}/notifications/${notificationId}/read`);
      fetchNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.put(`${API}/notifications/read-all`);
      fetchNotifications();
      toast.success('Tüm bildirimler okundu olarak işaretlendi');
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'record_approved':
        return <Check className="w-4 h-4 text-green-400" />;
      case 'record_rejected':
        return <X className="w-4 h-4 text-red-400" />;
      case 'missing_document':
        return <FileText className="w-4 h-4 text-yellow-400" />;
      case 'new_record':
        return <Clock className="w-4 h-4 text-blue-400" />;
      default:
        return <Bell className="w-4 h-4 text-zinc-400" />;
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Şimdi';
    if (minutes < 60) return `${minutes} dk önce`;
    if (hours < 24) return `${hours} saat önce`;
    return `${days} gün önce`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className={`relative w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
          theme === 'dark'
            ? 'bg-[#18181b] border border-[#27272a] hover:bg-[#27272a]'
            : 'bg-white border border-gray-200 hover:bg-gray-100'
        }`}
        data-testid="notification-bell"
      >
        <Bell className={`w-5 h-5 ${theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}`} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {showDropdown && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowDropdown(false)}
          />
          <div className={`absolute right-0 top-12 w-80 max-h-96 overflow-y-auto rounded-xl shadow-xl z-50 border ${
            theme === 'dark'
              ? 'bg-[#18181b] border-[#27272a]'
              : 'bg-white border-gray-200'
          }`}>
            {/* Header */}
            <div className={`sticky top-0 p-3 border-b flex items-center justify-between ${
              theme === 'dark' ? 'bg-[#18181b] border-[#27272a]' : 'bg-white border-gray-200'
            }`}>
              <h3 className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                Bildirimler
              </h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-[#FACC15] hover:underline flex items-center gap-1"
                >
                  <CheckCheck className="w-3 h-3" />
                  Tümünü Oku
                </button>
              )}
            </div>

            {/* Notifications List */}
            <div className="divide-y divide-[#27272a]">
              {notifications.length === 0 ? (
                <div className="p-6 text-center">
                  <Bell className={`w-8 h-8 mx-auto mb-2 ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`} />
                  <p className={`text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                    Bildirim yok
                  </p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => !notification.is_read && markAsRead(notification.id)}
                    className={`p-3 cursor-pointer transition-colors ${
                      !notification.is_read 
                        ? theme === 'dark' ? 'bg-[#27272a]/50' : 'bg-blue-50'
                        : ''
                    } ${theme === 'dark' ? 'hover:bg-[#27272a]' : 'hover:bg-gray-50'}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        theme === 'dark' ? 'bg-[#09090b]' : 'bg-gray-100'
                      }`}>
                        {getNotificationIcon(notification.notification_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                          {notification.message}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                            {notification.sender_name}
                          </span>
                          <span className={`text-xs ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`}>
                            •
                          </span>
                          <span className={`text-xs ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`}>
                            {formatTime(notification.created_at)}
                          </span>
                        </div>
                      </div>
                      {!notification.is_read && (
                        <span className="w-2 h-2 bg-[#FACC15] rounded-full flex-shrink-0" />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationBell;
