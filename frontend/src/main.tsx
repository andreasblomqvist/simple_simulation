import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './styles/globals.css';
import './lib/theme-script';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './components/providers/theme-provider';
import { YearNavigationProvider } from './components/v2/YearNavigationProvider';
import { ConfigProvider as CustomConfigProvider } from './components/ConfigContext';
import { Toaster } from './components/ui/toaster';
import { TooltipProvider } from './components/ui/tooltip';

// Import routing
import { EnhancedRoutes } from './routes/EnhancedRoutes';

function MainApp() {
  return (
    <BrowserRouter>
      <ThemeProvider 
        attribute="class"
        defaultTheme="dark" 
        storageKey="simplesim-ui-theme"
        enableSystem
      >
        <TooltipProvider>
          <CustomConfigProvider>
            <YearNavigationProvider>
              <EnhancedRoutes />
              <Toaster />
            </YearNavigationProvider>
          </CustomConfigProvider>
        </TooltipProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <MainApp />
  </React.StrictMode>
);
