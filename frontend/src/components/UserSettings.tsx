import React from 'react';
import { PageHeader, ComingSoonCard } from './ui';

export const UserSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="User Settings"
        description="Manage your profile, preferences, and application settings"
      />

      <ComingSoonCard
        icon="⚙️"
        title="User Settings"
        description="Customize your football simulation experience with personalized settings and preferences."
        features={[
          { label: 'Profile management' },
          { label: 'Simulation preferences' },
          { label: 'UI theme customization' },
          { label: 'Notification settings' }
        ]}
      />
    </div>
  );
};