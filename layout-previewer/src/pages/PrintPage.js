import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { DynamicGridLayout } from '@answerrocket/dynamic-layout';

const PrintPage = () => {
  const { '*': pageId } = useParams();
  const [pageDefinition, setPageDefinition] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadPageDefinition = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch(`/previews/${pageId}`)
        const def = await res.json()
        setPageDefinition(def);
      } catch (error) {
        console.error('Error loading page definition:', error);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadPageDefinition();
  }, [pageId]);

  // Memoize the callbacks to prevent unnecessary re-renders
  const handleElementSelect = React.useCallback(() => {}, []);
  const handleUpdateElement = React.useCallback(() => {}, []);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!pageDefinition) return <div>No page definition found</div>;

  return (
    <div className="print-page-container">
      <DynamicGridLayout 
        pageDefinition={pageDefinition}
        onElementSelect={handleElementSelect}
        onUpdateElement={handleUpdateElement}
        className="grid-layout-container"
      />
    </div>
  );
};


export default PrintPage;