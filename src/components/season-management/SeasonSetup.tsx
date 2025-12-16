import React, { useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';
import { ErrorMessage, Button } from '../ui';

const SeasonSetup: React.FC = observer(() => {
	const { appStore, seasonStore } = useContext(StoresContext);
	const { currentSeason, loading, error, organizedTeams, isSeasonComplete } = seasonStore;

	const handleCreateSeason = async () => {
		const result = await seasonStore.createSeason(2024, undefined, `NFL 2024 Season`);
		if (result.success) {
			appStore.setCurrentTab('Schedule');
		}
	};

	const handleStartNewSeason = async () => {
		const newYear = currentSeason ? currentSeason.year + 1 : new Date().getFullYear();
		const result = await seasonStore.startNewSeason(newYear);
		if (result.success) {
			appStore.setCurrentTab('Setup');
		}
	};

	const handleDebugSeasons = async () => {
		try {
			const result = await window.electronAPI.debug.listSeasons();
			console.log('🔍 [DEBUG] All seasons from debug call:', result);
		} catch (error) {
			console.error('❌ [DEBUG] Error listing seasons:', error);
		}
	};

	console.log('🔍 [CURRENT SEASON] currentSeason data:', currentSeason);
	console.log('🔍 [ORGANIZED TEAMS] organizedTeams data:', organizedTeams);

	return (
		<div className="space-y-6">
			{/* Season Status */}
			{currentSeason ? (
				<div className="space-y-4">
					<div className="card p-6">
						<div className="flex items-center justify-between">
							<div>
								<h2 className="text-xl font-semibold text-white mb-2">
									{currentSeason.year} Season
								</h2>
								<div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
									<div>
										<span className="text-secondary-400">Week:</span>
										<span className="text-white ml-2">{currentSeason.current_week}</span>
									</div>
									<div>
										<span className="text-secondary-400">Phase:</span>
										<span className="text-white ml-2 capitalize">
											{currentSeason.current_phase ? currentSeason.current_phase.replace('_', ' ') : ''}
										</span>
									</div>
									<div>
										<span className="text-secondary-400">Games:</span>
										<span className="text-white ml-2">{currentSeason.completed_games}/{currentSeason.total_games}</span>
									</div>
									<div>
										<span className="text-secondary-400">Progress:</span>
										<span className="text-white ml-2">{currentSeason.completion_percentage}%</span>
									</div>
								</div>
							</div>
							<div className="text-right">
								<div className="w-16 h-16 relative">
									<div className="w-full h-full rounded-full border-4 border-secondary-600 flex items-center justify-center">
										<span className="text-xs text-white font-semibold">
											{currentSeason.completion_percentage}%
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
					{/* New Season Button - Show when season is complete */}
					{isSeasonComplete && (
						<div className="card p-6 text-center">
							<div className="text-4xl mb-4">🏆</div>
							<h3 className="text-lg font-semibold text-white mb-2">Season Complete!</h3>
							<p className="text-secondary-400 mb-4">
								Ready to start the {currentSeason.year + 1} season?
							</p>
							<Button
								onClick={handleStartNewSeason}
								loading={loading}
							>
								Start {currentSeason.year + 1} Season
							</Button>
						</div>
					)}
				</div>
			) : (
				<div className="card p-8 text-center">
					<div className="text-6xl mb-4">🏈</div>
					<h2 className="text-xl font-semibold text-white mb-2">No Season Selected</h2>
					<p className="text-secondary-400 mb-6">
						Select a season from the dropdown above or create a new one to get started.
					</p>
					<Button
						onClick={handleCreateSeason}
						loading={loading}
					>
						Create 2024 Season
					</Button>
					<Button
						onClick={handleDebugSeasons}
						variant="secondary"
					>
						Debug: List All Seasons
					</Button>
				</div>
			)}
			{/* Teams Overview */}
			{Object.keys(organizedTeams).length > 0 && (
				<div className="card p-6">
					<h3 className="text-lg font-semibold text-white mb-4">League Structure</h3>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
						{Object.entries(organizedTeams).map(([conference, divisions]) => (
							<div key={conference} className="space-y-3">
								<h4 className="text-md font-semibold text-primary-400">{conference}</h4>
								{Object.entries(divisions).map(([division, divTeams]) => (
									<div key={division} className="ml-4">
										<h5 className="text-sm font-medium text-secondary-300 mb-1">{division}</h5>
										<div className="ml-4 space-y-1">
											{divTeams.map((team) => (
												<div key={team.abbreviation} className="text-sm text-secondary-400">
													{team.city} {team.name} ({team.abbreviation})
												</div>
											))}
										</div>
									</div>
								))}
							</div>
						))}
					</div>
				</div>
			)}
			<ErrorMessage message={error} />
		</div>
	);
});

export default SeasonSetup;
