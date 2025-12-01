import React, { useEffect, useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';
import { Button, Card } from '../ui';

const SeasonSchedule: React.FC = observer(() => {
	const { seasonStore } = useContext(StoresContext);
	const {
		currentSeason, currentWeekGames, selectedWeek,
		loading, error, scheduledGamesCount
	} = seasonStore;

	useEffect(() => {
		if (currentSeason) {
			seasonStore.loadNextGames();
			seasonStore.loadWeekGames(currentSeason.current_week);
		}
	}, [currentSeason]);

	const handleSimulateGame = async (gameId: string) => {
		await seasonStore.simulateGame(gameId);
		if (currentSeason) {
			await seasonStore.loadWeekGames(currentSeason.current_week);
		}
	};

	const handleSimulateWeek = async () => {
		if (!currentSeason) return;
		await seasonStore.simulateWeek(currentSeason.current_week);
		await seasonStore.loadWeekGames(currentSeason.current_week);
	};

	const handleLoadWeek = async (week: number) => {
		await seasonStore.loadWeekGames(week);
	};

	const canSimulateWeek = (week: number) => {
		if (!currentSeason) return false;
		return week <= currentSeason.current_week;
	};

	console.log('Current Season:', currentSeason);
	if (!currentSeason) {
		return (
			<div className="card p-8 text-center">
				<div className="text-6xl mb-4">📅</div>
				<h2 className="text-xl font-semibold text-white mb-2">No Active Season</h2>
				<p className="text-secondary-400">Create a season first to view the schedule.</p>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			<Card>
				<div className="flex flex-wrap items-center justify-between gap-4">
					<div>
						<h2 className="text-xl font-semibold text-white mb-1">Week {currentSeason.current_week}</h2>
						<p className="text-secondary-400">
							{scheduledGamesCount} games remaining to simulate
						</p>
					</div>
					<div className="flex flex-wrap gap-3">
						<Button
							onClick={handleSimulateWeek}
							disabled={loading || scheduledGamesCount === 0}
							loading={loading}
						>
							Simulate Week {currentSeason.current_week}
						</Button>
						<Button
							variant="secondary"
							onClick={async () => {
								await seasonStore.simulateToWeek(Math.min(currentSeason.current_week + 2, 18));
								if (currentSeason) {
									await seasonStore.loadWeekGames(seasonStore.currentSeason?.current_week || currentSeason.current_week);
								}
							}}
							disabled={loading || scheduledGamesCount === 0 || currentSeason.current_week >= 18}
						>
							Simulate 3 Weeks
						</Button>
						<Button
							variant="accent"
							onClick={async () => {
								await seasonStore.simulateFullSeason();
								if (seasonStore.currentSeason) {
									await seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
								}
							}}
							disabled={loading || currentSeason.current_phase !== 'regular_season' || scheduledGamesCount === 0}
						>
							Simulate Rest of Season
						</Button>
					</div>
				</div>
			</Card>
			<div className="card p-6">
				<h3 className="text-lg font-semibold text-white mb-4">Browse Schedule</h3>
				<div className="flex flex-wrap gap-2 mb-4">
					{Array.from({ length: 18 }, (_, i) => i + 1).map((week) => {
						const isCurrentWeek = week === currentSeason.current_week;
						const isPastWeek = week < currentSeason.current_week;
						const isFutureWeek = week > currentSeason.current_week;
						return (
							<button
								key={week}
								onClick={() => handleLoadWeek(week)}
								className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
									selectedWeek === week
										? 'bg-primary-600 text-white'
										: isPastWeek
										? 'bg-green-900 text-green-300 hover:bg-green-800'
										: isCurrentWeek
										? 'bg-yellow-900 text-yellow-300 hover:bg-yellow-800'
										: 'bg-secondary-700 text-secondary-300 hover:bg-secondary-600'
								}`}
								title={
									isPastWeek ? 'Completed week' :
									isCurrentWeek ? 'Current week' :
									'Future week'
								}
							>
								Week {week}
								{isPastWeek && ' ✓'}
								{isCurrentWeek && ' ⭐'}
							</button>
						);
					})}
				</div>
			</div>
			<div className="card p-6">
				<h3 className="text-lg font-semibold text-white mb-4">
					Week {selectedWeek} Games ({currentWeekGames.length})
				</h3>
				{currentWeekGames.length > 0 ? (
					<div className="space-y-3">
						{currentWeekGames.map((game) => (
							<div
								key={game.game_id}
								className="flex items-center justify-between p-4 bg-secondary-800 rounded-lg"
							>
								<div className="flex-1">
									<div className="flex items-center space-x-4">
										<div className="text-center min-w-0 flex-1">
											<p className="text-sm text-secondary-400">Away</p>
											<p className="font-semibold text-white truncate">
												{game.away_team.city} {game.away_team.name}
											</p>
											{game.away_score !== undefined && (
												<p className="text-lg font-bold text-white">{game.away_score}</p>
											)}
										</div>
										<div className="text-secondary-400 font-medium">@</div>
										<div className="text-center min-w-0 flex-1">
											<p className="text-sm text-secondary-400">Home</p>
											<p className="font-semibold text-white truncate">
												{game.home_team.city} {game.home_team.name}
											</p>
											{game.home_score !== undefined && (
												<p className="text-lg font-bold text-white">{game.home_score}</p>
											)}
										</div>
									</div>
								</div>
								<div className="flex items-center space-x-3">
									{game.status === 'completed' ? (
										<div className="text-center">
											<span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-300">
												Final{game.overtime && ' (OT)'}
											</span>
											{game.winner && (
												<p className="text-xs text-secondary-400 mt-1">
													Winner: {game.winner}
												</p>
											)}
										</div>
									) : (
										<button
											onClick={() => handleSimulateGame(game.game_id)}
											disabled={loading}
											className="btn-secondary text-sm"
										>
											Simulate
										</button>
									)}
								</div>
							</div>
						))}
					</div>
				) : (
					<p className="text-secondary-400 text-center py-8">No games scheduled for this week.</p>
				)}
			</div>
			{error && (
				<div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
					<p className="text-red-200">{error}</p>
				</div>
			)}
		</div>
	);
});

export default SeasonSchedule;
