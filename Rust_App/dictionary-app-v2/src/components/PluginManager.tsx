import { useEffect, useState } from 'react';
import { PluginInfo } from '../types';
import DictionaryAPI from '../utils/api';

interface PluginManagerProps {
  className?: string;
}

export function PluginManager({ className = '' }: PluginManagerProps) {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await DictionaryAPI.getPlugins();
      if (response.success) {
        setPlugins(response.data);
      } else {
        setError(response.error.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  };

  const togglePlugin = async (pluginId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await DictionaryAPI.enablePlugin(pluginId);
      } else {
        await DictionaryAPI.disablePlugin(pluginId);
      }
      await loadPlugins(); // Reload to get updated state
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${enabled ? 'enable' : 'disable'} plugin`);
    }
  };

  if (loading) {
    return (
      <div className={`plugin-manager ${className}`}>
        <div className="loading">Loading plugins...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`plugin-manager ${className}`}>
        <div className="error">Error: {error}</div>
        <button onClick={loadPlugins}>Retry</button>
      </div>
    );
  }

  const pluginManagerStyle: React.CSSProperties = {
    background: '#f8f9fa',
    borderRadius: '8px',
    padding: '16px',
    margin: '16px 0',
  };

  const pluginHeaderStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    borderBottom: '1px solid #dee2e6',
    paddingBottom: '8px',
  };

  const buttonStyle: React.CSSProperties = {
    background: '#007bff',
    color: 'white',
    border: 'none',
    padding: '4px 12px',
    borderRadius: '4px',
    cursor: 'pointer',
  };

  const pluginItemStyle: React.CSSProperties = {
    background: 'white',
    border: '1px solid #dee2e6',
    borderRadius: '6px',
    padding: '12px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  };

  const pluginInfoStyle: React.CSSProperties = {
    flex: 1,
  };

  const pluginMetaStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    fontSize: '12px',
    color: '#868e96',
    marginTop: '8px',
  };

  return (
    <div className={className} style={pluginManagerStyle}>
      <div style={pluginHeaderStyle}>
        <h3 style={{ margin: 0, color: '#343a40' }}>Plugin Manager</h3>
        <button onClick={loadPlugins} style={buttonStyle}>
          Refresh
        </button>
      </div>
      
      {plugins.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#6c757d' }}>
          No plugins found
        </div>
      ) : (
        <div>
          {plugins.map((plugin) => (
            <div key={plugin.manifest.id} style={pluginItemStyle}>
              <div style={pluginInfoStyle}>
                <div style={{ fontWeight: 600, color: '#343a40', marginBottom: '4px' }}>
                  {plugin.manifest.name}
                </div>
                <div style={{ color: '#6c757d', fontSize: '14px', marginBottom: '8px' }}>
                  {plugin.manifest.description}
                </div>
                <div style={pluginMetaStyle}>
                  <span style={{ background: '#e9ecef', padding: '2px 6px', borderRadius: '3px' }}>
                    v{plugin.manifest.version}
                  </span>
                  {plugin.manifest.author && (
                    <span>by {plugin.manifest.author}</span>
                  )}
                  <span style={{ color: plugin.loaded ? '#28a745' : '#ffc107' }}>
                    {plugin.loaded ? 'Loaded' : 'Not Loaded'}
                  </span>
                </div>
                {plugin.error && (
                  <div style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                    Error: {plugin.error}
                  </div>
                )}
              </div>
              
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={plugin.manifest.enabled}
                    onChange={(e) => togglePlugin(plugin.manifest.id, e.target.checked)}
                    style={{ margin: 0 }}
                  />
                  Enabled
                </label>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PluginManager;