import React, { useState } from "react";
import { Bell, Shield, Database, Monitor } from "lucide-react";

function Toggle({ checked, onChange, label }) {
  return (
    <label className="flex items-center justify-between gap-4 py-3 cursor-pointer group">
      <span className="text-sm font-medium text-gray-700 dark:text-neutral-200 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
        {label}
      </span>
      <span className="relative inline-flex h-6 w-11 shrink-0 rounded-full overflow-hidden">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only peer"
        />
        <span className="absolute inset-0 rounded-full border border-gray-300 dark:border-neutral-600 transition-colors duration-200 peer-checked:border-red-500" />
        <span className="absolute inset-0 rounded-full bg-gray-200 dark:bg-neutral-600 transition-colors duration-200 peer-checked:bg-red-500" />
        <span
          className="absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white dark:bg-neutral-100 shadow transition-all duration-200 pointer-events-none
            peer-checked:left-[22px]
            peer-focus-visible:ring-2 peer-focus-visible:ring-red-500 peer-focus-visible:ring-offset-2 dark:peer-focus-visible:ring-offset-neutral-900"
        />
      </span>
    </label>
  );
}

function SettingsSection({ icon: Icon, title, description, children }) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800/50 shadow-sm overflow-hidden">
      <div className="p-5 border-b border-gray-100 dark:border-neutral-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-red-50 dark:bg-red-500/20">
            <Icon className="w-5 h-5 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {title}
            </h2>
            <p className="text-sm text-gray-500 dark:text-neutral-400 mt-0.5">
              {description}
            </p>
          </div>
        </div>
      </div>
      <div className="p-5 space-y-1">
        {children}
      </div>
    </div>
  );
}

export default function Settings() {
  const [notifications, setNotifications] = useState({
    criticalAlerts: true,
    dispatchConfirmations: true,
    shiftReminders: true,
  });
  const [security, setSecurity] = useState({
    twoFactorAuth: true,
    sessionTimeout: true,
    auditLogging: true,
  });
  const [data, setData] = useState({
    autoSyncPredictions: true,
    dataRetention: true,
    exportReports: true,
  });
  const [display, setDisplay] = useState({
    compactTableView: true,
    animationEffects: true,
    realTimeUpdates: true,
  });
  const [refreshInterval, setRefreshInterval] = useState(30);

  return (
<<<<<<< HEAD
    <div className="min-h-screen bg-[#F4F6F8] dark:bg-[#0F172A] text-gray-900 dark:text-slate-100 p-4 sm:p-6 transition-colors duration-300">
=======
    <div className="min-h-screen bg-[#F4F6F8] dark:bg-[#0F172A] text-gray-900 dark:text-neutral-100 p-6 transition-colors duration-300">
>>>>>>> dev
      {/* Header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Settings
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-neutral-400">
          System configuration and preferences
        </p>
      </div>

      <div className="w-full space-y-4 sm:space-y-6">
        {/* Notifications */}
        <SettingsSection
          icon={Bell}
          title="Notifications"
          description="Alert settings for critical incidents"
        >
          <Toggle
            label="Critical alerts"
            checked={notifications.criticalAlerts}
            onChange={(v) =>
              setNotifications((s) => ({ ...s, criticalAlerts: v }))
            }
          />
          <Toggle
            label="Dispatch confirmations"
            checked={notifications.dispatchConfirmations}
            onChange={(v) =>
              setNotifications((s) => ({ ...s, dispatchConfirmations: v }))
            }
          />
          <Toggle
            label="Shift reminders"
            checked={notifications.shiftReminders}
            onChange={(v) =>
              setNotifications((s) => ({ ...s, shiftReminders: v }))
            }
          />
        </SettingsSection>

        {/* Security */}
        <SettingsSection
          icon={Shield}
          title="Security"
          description="Authentication and access control"
        >
          <Toggle
            label="Two-factor auth"
            checked={security.twoFactorAuth}
            onChange={(v) => setSecurity((s) => ({ ...s, twoFactorAuth: v }))}
          />
          <Toggle
            label="Session timeout (30 min)"
            checked={security.sessionTimeout}
            onChange={(v) =>
              setSecurity((s) => ({ ...s, sessionTimeout: v }))
            }
          />
          <Toggle
            label="Audit logging"
            checked={security.auditLogging}
            onChange={(v) => setSecurity((s) => ({ ...s, auditLogging: v }))}
          />
        </SettingsSection>

        {/* Data */}
        <SettingsSection
          icon={Database}
          title="Data"
          description="Model and data management"
        >
          <Toggle
            label="Auto-sync predictions"
            checked={data.autoSyncPredictions}
            onChange={(v) =>
              setData((s) => ({ ...s, autoSyncPredictions: v }))
            }
          />
          <Toggle
            label="Data retention (90 days)"
            checked={data.dataRetention}
            onChange={(v) =>
              setData((s) => ({ ...s, dataRetention: v }))
            }
          />
          <Toggle
            label="Export reports"
            checked={data.exportReports}
            onChange={(v) =>
              setData((s) => ({ ...s, exportReports: v }))
            }
          />
        </SettingsSection>

        {/* Display */}
        <SettingsSection
          icon={Monitor}
          title="Display"
          description="Dashboard preferences"
        >
          <Toggle
            label="Compact table view"
            checked={display.compactTableView}
            onChange={(v) =>
              setDisplay((s) => ({ ...s, compactTableView: v }))
            }
          />
          <Toggle
            label="Animation effects"
            checked={display.animationEffects}
            onChange={(v) =>
              setDisplay((s) => ({ ...s, animationEffects: v }))
            }
          />
          <Toggle
            label="Real-time updates"
            checked={display.realTimeUpdates}
            onChange={(v) =>
              setDisplay((s) => ({ ...s, realTimeUpdates: v }))
            }
          />
          <div className="pt-3">
            <div className="flex items-center justify-between gap-4 mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-neutral-200">
                Refresh interval (seconds)
              </span>
              <span className="text-sm text-gray-500 dark:text-neutral-400 tabular-nums">
                {refreshInterval}s
              </span>
            </div>
            <input
              type="range"
              min={5}
              max={120}
              step={5}
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="w-full h-2 rounded-full appearance-none bg-gray-200 dark:bg-neutral-600 accent-red-500
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-red-500 [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:shadow [&::-webkit-slider-thumb]:border-0"
            />
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}
