import React, { useEffect, useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';
import { Button, Card } from '../ui';

const SeasonPlayoffs: React.FC = observer(() => {
	const { seasonStore } = useContext(StoresContext);
	const {
		currentSeason, playoffBracket, nextPlayoffGames, 
		loading, error
	} = seasonStore;

	useEffect(() => {
		seasonStore.loadPlayoffBracket();
		seasonStore.loadNextPlayoffGames();
	}, [seasonStore]);

	const handleSimulatePlayoffGame = async (gameId: string) => {
		await seasonStore.simulatePlayoffGame(gameId);
		await seasonStore.loadPlayoffBracket();
		await seasonStore.loadNextPlayoffGames();
	};

	if (!currentSeason || !playoffBracket) {
		return (
			<div className="card p-8 text-center">
				<div className="text-6xl mb-4">🏆</div>
				<h2 className="text-xl font-semibold text-white mb-2">No Playoff Data</h2>
				<p className="text-secondary-400">Simulate the regular season to generate playoff matchups.</p>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			<Card>
				<div className="flex items-center justify-between">
					<h2 className="text-xl font-semibold text-white mb-1">Playoff Bracket</h2>
					<Button
						onClick={() => seasonStore.loadPlayoffBracket()}
						loading={loading}
					>
						Refresh Bracket
					</Button>
				</div>
			</Card>
			<div className="card p-6">
				<h3 className="text-lg font-semibold text-white mb-4">Upcoming Playoff Games</h3>
				{nextPlayoffGames.length > 0 ? (
					<div className="space-y-3">
						{nextPlayoffGames.map((game) => (
							<div
								key={game.game_id}
								className="flex items-center justify-between p-4 bg-secondary-800 rounded-lg"
							>
								<div className="flex-1">
									<div className="flex items-center space-x-4">
										<div className="text-center min-w-0 flex-1">
											<p className="text-sm text-secondary-400">Away</p>
											<p className="font-semibold text-white truncate">
												{game.away_team?.city} {game.away_team?.name}
											</p>
											{game.away_score !== undefined && (
												<p className="text-lg font-bold text-white">{game.away_score}</p>
											)}
										</div>
										<div className="text-secondary-400 font-medium">@</div>
										<div className="text-center min-w-0 flex-1">
											<p className="text-sm text-secondary-400">Home</p>
											<p className="font-semibold text-white truncate">
												{game.home_team?.city} {game.home_team?.name}
											</p>
											{game.home_score !== undefined && (
												<p className="text-lg font-bold text-white">{game.home_score}</p>
											)}
										</div>
									</div>
								</div>
								<div className="flex items-center space-x-3">
									{game.completed ? (
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
											onClick={() => handleSimulatePlayoffGame(game.game_id)}
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
					<p className="text-secondary-400 text-center py-8">No playoff games scheduled.</p>
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

export default SeasonPlayoffs;
