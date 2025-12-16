import React, { useEffect, useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';
import { Button, Card } from '../ui';
import type { PlayoffGame } from '../../stores/SeasonStore';

interface BracketGameProps {
	game: PlayoffGame | null;
	onSimulate?: (gameId: string) => void;
	loading?: boolean;
}

const BracketGame: React.FC<BracketGameProps> = ({ game, onSimulate, loading }) => {
	if (!game || !game.home_team || !game.away_team) {
		return (
			<div className="bg-secondary-800/50 rounded-lg p-3 border-2 border-dashed border-secondary-700 min-h-[100px] flex items-center justify-center">
				<p className="text-xs text-secondary-500">TBD</p>
			</div>
		);
	}

	const isWinner = (teamAbbr: string) => {
		if (!game.completed) return false;
		const homeWon = (game.home_score || 0) > (game.away_score || 0);
		return (homeWon && game.home_team?.abbreviation === teamAbbr) || 
		       (!homeWon && game.away_team?.abbreviation === teamAbbr);
	};

	const getTeamStyle = (teamAbbr: string) => {
		const winner = isWinner(teamAbbr);
		return winner ? 'text-white font-bold' : game.completed ? 'text-secondary-500' : 'text-white';
	};

	return (
		<div className="bg-secondary-800 rounded-lg border-2 border-secondary-700 overflow-hidden">
			<div className="p-3 space-y-2">
				{/* Away Team */}
				<div className={`flex items-center justify-between ${getTeamStyle(game.away_team?.abbreviation || '')}`}>
					<div className="flex items-center space-x-2 flex-1 min-w-0">
						<span className="text-xs font-mono text-secondary-400">
							{game.lower_seed?.seed || ''}
						</span>
						<span className="text-sm truncate">
							{game.away_team?.abbreviation}
						</span>
					</div>
					<span className="text-lg font-bold ml-2">
						{game.away_score !== undefined ? game.away_score : '-'}
					</span>
					{isWinner(game.away_team?.abbreviation || '') && (
						<span className="ml-1 text-green-400">✓</span>
					)}
				</div>
				
				{/* Home Team */}
				<div className={`flex items-center justify-between ${getTeamStyle(game.home_team?.abbreviation || '')}`}>
					<div className="flex items-center space-x-2 flex-1 min-w-0">
						<span className="text-xs font-mono text-secondary-400">
							{game.higher_seed?.seed || ''}
						</span>
						<span className="text-sm truncate">
							{game.home_team?.abbreviation}
						</span>
					</div>
					<span className="text-lg font-bold ml-2">
						{game.home_score !== undefined ? game.home_score : '-'}
					</span>
					{isWinner(game.home_team?.abbreviation || '') && (
						<span className="ml-1 text-green-400">✓</span>
					)}
				</div>
			</div>

			{/* Action Button */}
			{!game.completed && game.is_ready_to_play && onSimulate && (
				<div className="border-t border-secondary-700 p-2">
					<button
						onClick={() => onSimulate(game.game_id)}
						disabled={loading}
						className="w-full btn-primary text-xs py-1"
					>
						Simulate
					</button>
				</div>
			)}
			
			{game.completed && (
				<div className="border-t border-secondary-700 p-2 text-center">
					<span className="text-xs text-green-400 font-medium">
						Final{game.overtime ? ' (OT)' : ''}
					</span>
				</div>
			)}
		</div>
	);
};

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
		console.log('Simulating playoff game with ID:', gameId);
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

	const { wild_card_games, divisional_games, conference_championship_games, super_bowl } = playoffBracket;

	// Organize games by conference
	const afcWildCard = wild_card_games.filter(g => g.conference === 'AFC');
	const nfcWildCard = wild_card_games.filter(g => g.conference === 'NFC');
	const afcDivisional = divisional_games.filter(g => g.conference === 'AFC');
	const nfcDivisional = divisional_games.filter(g => g.conference === 'NFC');
	const afcChampionship = conference_championship_games.find(g => g.conference === 'AFC');
	const nfcChampionship = conference_championship_games.find(g => g.conference === 'NFC');

	return (
		<div className="space-y-6">
			<Card>
				<div className="flex items-center justify-between">
					<div>
						<h2 className="text-xl font-semibold text-white mb-1">🏆 Playoff Bracket</h2>
						<p className="text-sm text-secondary-400">
							Current Round: <span className="text-white font-medium">{playoffBracket.current_round.replace(/_/g, ' ').toUpperCase()}</span>
						</p>
					</div>
					<Button
						onClick={() => { seasonStore.loadPlayoffBracket();seasonStore.loadNextPlayoffGames(); }}
						loading={loading}
					>
						Refresh Bracket
					</Button>
				</div>
			</Card>

			{/* Bracket Visualization */}
			<div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
				{/* AFC Bracket */}
				<Card>
					<h3 className="text-lg font-semibold text-white mb-4 flex items-center">
						<span className="bg-blue-900/50 text-blue-300 px-2 py-1 rounded text-sm mr-2">AFC</span>
						American Football Conference
					</h3>
					
					<div className="space-y-6">
						{/* AFC Wild Card Round */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">Wild Card Round</h4>
							<div className="space-y-2">
								{afcWildCard.map((game, idx) => (
									<BracketGame 
										key={game.game_id || idx} 
										game={game} 
										onSimulate={handleSimulatePlayoffGame}
										loading={loading}
									/>
								))}
								{afcWildCard.length === 0 && (
									<p className="text-xs text-secondary-500 text-center py-4">No games scheduled</p>
								)}
							</div>
						</div>

						{/* AFC Divisional Round */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">Divisional Round</h4>
							<div className="space-y-2">
								{afcDivisional.map((game, idx) => (
									<BracketGame 
										key={game.game_id || idx} 
										game={game} 
										onSimulate={handleSimulatePlayoffGame}
										loading={loading}
									/>
								))}
								{afcDivisional.length === 0 && (
									<p className="text-xs text-secondary-500 text-center py-4">Awaiting Wild Card results</p>
								)}
							</div>
						</div>

						{/* AFC Championship */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">AFC Championship</h4>
							<BracketGame 
								game={afcChampionship || null} 
								onSimulate={handleSimulatePlayoffGame}
								loading={loading}
							/>
						</div>
					</div>
				</Card>

				{/* NFC Bracket */}
				<Card>
					<h3 className="text-lg font-semibold text-white mb-4 flex items-center">
						<span className="bg-red-900/50 text-red-300 px-2 py-1 rounded text-sm mr-2">NFC</span>
						National Football Conference
					</h3>
					
					<div className="space-y-6">
						{/* NFC Wild Card Round */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">Wild Card Round</h4>
							<div className="space-y-2">
								{nfcWildCard.map((game, idx) => (
									<BracketGame 
										key={game.game_id || idx} 
										game={game} 
										onSimulate={handleSimulatePlayoffGame}
										loading={loading}
									/>
								))}
								{nfcWildCard.length === 0 && (
									<p className="text-xs text-secondary-500 text-center py-4">No games scheduled</p>
								)}
							</div>
						</div>

						{/* NFC Divisional Round */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">Divisional Round</h4>
							<div className="space-y-2">
								{nfcDivisional.map((game, idx) => (
									<BracketGame 
										key={game.game_id || idx} 
										game={game} 
										onSimulate={handleSimulatePlayoffGame}
										loading={loading}
									/>
								))}
								{nfcDivisional.length === 0 && (
									<p className="text-xs text-secondary-500 text-center py-4">Awaiting Wild Card results</p>
								)}
							</div>
						</div>

						{/* NFC Championship */}
						<div>
							<h4 className="text-sm font-medium text-secondary-400 mb-3">NFC Championship</h4>
							<BracketGame 
								game={nfcChampionship || null} 
								onSimulate={handleSimulatePlayoffGame}
								loading={loading}
							/>
						</div>
					</div>
				</Card>
			</div>

			{/* Super Bowl */}
			{super_bowl && (
				<Card>
					<div className="text-center">
						<h3 className="text-2xl font-bold text-white mb-6 flex items-center justify-center">
							<span className="text-3xl mr-2">🏆</span>
							Super Bowl {playoffBracket.season_year}
						</h3>
						<div className="max-w-md mx-auto">
							<BracketGame 
								game={super_bowl} 
								onSimulate={handleSimulatePlayoffGame}
								loading={loading}
							/>
						</div>
						{super_bowl.completed && playoffBracket.super_bowl_champion && (
							<div className="mt-6 p-4 bg-yellow-900/20 border-2 border-yellow-600 rounded-lg">
								<p className="text-yellow-400 font-bold text-lg">
									🏆 Champion: {playoffBracket.super_bowl_champion.team.city} {playoffBracket.super_bowl_champion.team.name}
								</p>
							</div>
						)}
					</div>
				</Card>
			)}

			{error && (
				<div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
					<p className="text-red-200">{error}</p>
				</div>
			)}
		</div>
	);
});

export default SeasonPlayoffs;
