import React, { useEffect, useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';
import { PageHeader } from '../ui';
import SeasonSetup from './SeasonSetup';
import SeasonSchedule from './SeasonSchedule';
import SeasonStandings from './SeasonStandings';
import SeasonPlayoffs from './SeasonPlayoffs';

const SeasonManagement: React.FC = observer(() => {
	const { appStore, seasonStore } = useContext(StoresContext);
	const { currentSection } = appStore;
	const activeTab = appStore.currentTab || 'Setup';

	useEffect(() => {
		if (currentSection === 'season') {
			const loadInitialData = async () => {
				await seasonStore.fetchAllSeasons();
				if (seasonStore.selectedSeasonId) {
					await seasonStore.loadSeasonStatus(seasonStore.selectedSeasonId);
				}
				await seasonStore.loadTeams();
			};
			loadInitialData();
		}
	}, [currentSection, seasonStore]);

	useEffect(() => {
		if (seasonStore.selectedSeasonId) {
			seasonStore.loadSeasonStatus(seasonStore.selectedSeasonId);
			seasonStore.loadNextGames();
			if (seasonStore.currentSeason) {
				seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
				seasonStore.loadStandings(true);
			}
		}
	}, [seasonStore.selectedSeasonId]);

	useEffect(() => {
		if (currentSection === 'season') {
			seasonStore.setError(null);
		}
	}, [currentSection, seasonStore]);

	useEffect(() => {
		if (activeTab === 'Schedule' && seasonStore.currentSeason) {
			seasonStore.loadNextGames();
			seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
		}
	}, [activeTab, seasonStore]);

	const tabs = appStore.sectionTabs;

	const renderContent = () => {
		switch (activeTab) {
			case 'Setup':
				return <SeasonSetup />;
			case 'Schedule':
				return <SeasonSchedule />;
			case 'Standings':
				return <SeasonStandings />;
			case 'Playoffs':
				return <SeasonPlayoffs />;
			default:
				return <SeasonSetup />;
		}
	};

	const handleSeasonChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
		seasonStore.setSelectedSeason(e.target.value);
	};

	return (
		<div className="space-y-6">
			<PageHeader
				title="Season Simulation"
				description="Manage and simulate complete NFL seasons with comprehensive statistics"
			/>
			<div className="flex items-center gap-4">
				<label htmlFor="season-select" className="text-secondary-300 font-medium">
					Select Season:
				</label>
				<select
					id="season-select"
					value={seasonStore.selectedSeasonId || ''}
					onChange={handleSeasonChange}
					className="bg-secondary-800 text-white rounded px-3 py-2"
					disabled={seasonStore.allSeasons.length === 0}
				>
					{seasonStore.allSeasons.length === 0 ? (
						<option value="">No seasons available</option>
					) : (
						seasonStore.allSeasons.map(season => (
							<option key={season.id} value={season.id}>
								{season.season_year} ({season.schedule_type})
							</option>
						))
					)}
				</select>
			</div>
			<div className="flex space-x-1 bg-secondary-800 p-1 rounded-lg">
				{tabs.map((tab) => (
					<button
						key={tab}
						onClick={() => appStore.setCurrentTab(tab)}
						className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
							activeTab === tab
								? 'bg-primary-600 text-white'
								: 'text-secondary-300 hover:text-white hover:bg-secondary-700'
						}`}
					>
						{tab}
					</button>
				))}
			</div>
			{seasonStore.allSeasons.length === 0 ? (
				// When no seasons exist, always show the Setup tab (which has season creation)
				<SeasonSetup />
			) : (
				renderContent()
			)}
		</div>
	);
});

export default SeasonManagement;
