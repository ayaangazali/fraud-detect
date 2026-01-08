import React from 'react';
import { FileQuestion, Inbox } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 text-muted-foreground">
          {icon || <Inbox className="h-12 w-12" />}
        </div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground mb-4 max-w-sm">{description}</p>
        {action}
      </CardContent>
    </Card>
  );
};

export const NoDataState: React.FC = () => (
  <EmptyState
    icon={<FileQuestion className="h-12 w-12" />}
    title="No data available"
    description="There are no records to display at this time."
  />
);

export const NoResultsState: React.FC = () => (
  <EmptyState
    icon={<FileQuestion className="h-12 w-12" />}
    title="No results found"
    description="Try adjusting your search or filter criteria."
  />
);
