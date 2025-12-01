import React, { useEffect, useContext } from 'react';
import { observer } from 'mobx-react-lite';
import { StoresContext } from '../../stores';

const SeasonStandings: React.FC = observer(() => {
	const { seasonStore } = useContext(StoresContext);
	const { standings, standingsByDivision, loading, error } = seasonStore;

	useEffect(() => {
		seasonStore.loadStandings(true);
	}, []);

	const toggleStandingsView = async () => {
		const newView = !standingsByDivision;
		await seasonStore.loadStandings(newView);
	};

	return (
		<div className="space-y-6">
			<div className="card p-6">
				<div className="flex items-center justify-between">
					<h2 className="text-xl font-semibold text-white">League Standings</h2>
					<button
						onClick={toggleStandingsView}
						className="btn-secondary"
					>
						View by {standingsByDivision ? 'Conference' : 'Division'}
					</button>
				</div>
			</div>
			{Object.keys(standings).length > 0 ? (
				<div className="space-y-6">
					{Object.entries(standings).map(([divisionOrConf, teams]) => (
						<div key={divisionOrConf} className="card p-6">
							<h3 className="text-lg font-semibold text-white mb-4">{divisionOrConf}</h3>
							<div className="overflow-x-auto">
								<table className="w-full text-sm">
									<thead>
										<tr className="border-b border-secondary-600">
											<th className="text-left py-2 text-secondary-400">Team</th>
											<th className="text-center py-2 text-secondary-400">W</th>
											<th className="text-center py-2 text-secondary-400">L</th>
											<th className="text-center py-2 text-secondary-400">T</th>
											<th className="text-center py-2 text-secondary-400">PCT</th>
											<th className="text-center py-2 text-secondary-400">PF</th>
											<th className="text-center py-2 text-secondary-400">PA</th>
											<th className="text-center py-2 text-secondary-400">DIFF</th>
											<th className="text-center py-2 text-secondary-400">DIV</th>
											<th className="text-center py-2 text-secondary-400">CONF</th>
										</tr>
									</thead>
									<tbody>
										{teams.map((team, index) => (
											<tr key={team.team.abbreviation} className="border-b border-secondary-700/50">
												<td className="py-2">
													<div className="flex items-center">
														<span className="w-6 text-secondary-400 text-xs">{index + 1}</span>
														<span className="font-medium text-white">
															{team.team.city} {team.team.name}
														</span>
														<span className="ml-2 text-secondary-400">({team.team.abbreviation})
														</span>
													</div>
												</td>
												<td className="text-center py-2 text-white font-medium">{team.wins}</td>
												<td className="text-center py-2 text-white font-medium">{team.losses}</td>
												<td className="text-center py-2 text-white font-medium">{team.ties}</td>
												<td className="text-center py-2 text-white font-medium">{team.win_percentage}</td>
												<td className="text-center py-2 text-secondary-300">{team.points_for}</td>
												<td className="text-center py-2 text-secondary-300">{team.points_against}</td>
												<td className={`text-center py-2 font-medium ${
													team.point_differential > 0 
														? 'text-green-400' 
														: team.point_differential < 0 
														? 'text-red-400' 
														: 'text-secondary-300'
												}`}>
													{team.point_differential > 0 ? '+' : ''}{team.point_differential}
												</td>
												<td className="text-center py-2 text-secondary-300">{team.division_record}</td>
												<td className="text-center py-2 text-secondary-300">{team.conference_record}</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</div>
					))}
				</div>
			) : (
				<div className="card p-8 text-center">
					<div className="text-6xl mb-4">📊</div>
					<h2 className="text-xl font-semibold text-white mb-2">No Standings Available</h2>
					<p className="text-secondary-400">Create and simulate some games to see standings.</p>
				</div>
			)}
			{error && (
				<div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
					<p className="text-red-200">{error}</p>
				</div>
			)}
		</div>
	);
});

export default SeasonStandings;
