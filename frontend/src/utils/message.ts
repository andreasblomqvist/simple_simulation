import { toast } from '../components/ui/use-toast';

// shadcn/ui toast wrapper to replace Ant Design message
export const showMessage = {
  success: (content: string, duration?: number) => {
    toast({
      title: "Success",
      description: content,
      variant: "default",
      duration: duration || 3000,
    });
  },
  error: (content: string, duration?: number) => {
    toast({
      title: "Error", 
      description: content,
      variant: "destructive",
      duration: duration || 5000,
    });
  },
  warning: (content: string, duration?: number) => {
    toast({
      title: "Warning",
      description: content,
      variant: "default",
      duration: duration || 4000,
    });
  },
  info: (content: string, duration?: number) => {
    toast({
      title: "Info",
      description: content,
      variant: "default", 
      duration: duration || 3000,
    });
  },
  loading: (content: string, duration?: number) => {
    toast({
      title: "Loading",
      description: content,
      variant: "default",
      duration: duration || 2000,
    });
  }
};

// Export the toast function for direct usage
export { toast };