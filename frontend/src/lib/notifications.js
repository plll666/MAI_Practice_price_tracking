// Browser push notifications service

const NOTIFICATION_PERMISSION_KEY = 'notification_permission';

export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('Browser does not support notifications');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    localStorage.setItem(NOTIFICATION_PERMISSION_KEY, permission);
    return permission === 'granted';
  }

  return false;
};

export const showBrowserNotification = (title, options = {}) => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    return null;
  }

  const notification = new Notification(title, {
    icon: '/vite.svg',
    badge: '/vite.svg',
    ...options
  });

  setTimeout(() => notification.close(), 10000);

  notification.onclick = () => {
    window.focus();
    notification.close();
    if (options.url) {
      window.location.href = options.url;
    }
  };

  return notification;
};

export const getNotificationPermission = () => {
  if (!('Notification' in window)) {
    return 'unsupported';
  }
  return Notification.permission;
};
