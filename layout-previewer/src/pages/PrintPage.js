import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { DynamicGridLayout } from '@answerrocket/dynamic-layout';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';

const initHighcharts = () => {
  if (typeof Highcharts === 'object') {
    HighchartsMore(Highcharts);
    console.log('Highcharts More module initialized');
  } else {
    console.error('Highcharts not loaded');
  }
};

const PrintPage = () => {
  const { '*': pageId } = useParams();
  const [visualizations, setVisualizations] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [highchartsInitialized, setHighchartsInitialized] = useState(false);

  useEffect(() => {
    if (!highchartsInitialized) {
      initHighcharts();
      setHighchartsInitialized(true);
    }
  }, [highchartsInitialized]);

  useEffect(() => {
    const loadVisualizations = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch(`/previews/${pageId}`)
        const def = await res.json()
        setVisualizations(def);
      } catch (error) {
        console.error('Error loading page definition:', error);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadVisualizations();
  }, [pageId]);

  // Memoize the callbacks to prevent unnecessary re-renders
  const handleElementSelect = React.useCallback(() => {}, []);
  const handleUpdateElement = React.useCallback(() => {}, []);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!visualizations) return <div>No page definition found</div>;

  const titles = visualizations.map(viz => viz.title)
  const layouts = visualizations.map(viz => viz.layout)

  return (
    <div className="print-page-container">
      <Tabs>
        <TabList>
        {titles.map((title) => 
          <Tab>{title}</Tab>
        )}
        </TabList>
        {layouts.map((layout) => 
          <TabPanel>
            <DynamicGridLayout 
              pageDefinition={layout}
              onElementSelect={handleElementSelect}
              onUpdateElement={handleUpdateElement}
              className="grid-layout-container"
            />
          </TabPanel>
        )}

      </Tabs>
    </div>
  );
};


export default PrintPage;