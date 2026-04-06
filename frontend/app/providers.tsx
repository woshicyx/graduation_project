'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { UserProvider } from '@/components/user-auth-context';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1分钟
            gcTime: 5 * 60 * 1000, // 5分钟
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <UserProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </UserProvider>
  );
}
